"""
メッセージングAPIエンドポイントのテスト
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi import status

from app.schemas.message import MessageContentType


class TestMessageEndpoints:
    """メッセージ関連エンドポイントのテスト"""

    def test_send_message(self, client, sample_user1, sample_user2):
        """メッセージ送信エンドポイント"""
        mock_message_service = AsyncMock()
        mock_message_service.send_message.return_value = AsyncMock(
            message_id="message_123",
            conversation_id=f"{sample_user1.uid}_{sample_user2.uid}",
            sender_id=sample_user1.uid,
            recipient_id=sample_user2.uid,
            content="こんにちは！",
            content_type=MessageContentType.TEXT,
            is_visible_to_recipient=False,
            is_read=False,
            created_at=datetime.utcnow(),
            read_at=None,
            revealed_at=None,
            sender_display_name=sample_user1.display_name,
            sender_profile_image_url=None,
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages",
                json={
                    "recipient_id": sample_user2.uid,
                    "content": "こんにちは！",
                    "content_type": "text",
                },
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["message_id"] == "message_123"
            assert data["sender_id"] == sample_user1.uid
            assert data["recipient_id"] == sample_user2.uid
            assert data["content"] == "こんにちは！"
            assert data["is_visible_to_recipient"] is False
            assert data["is_read"] is False

    def test_send_message_to_self_error(self, client):
        """自分自身へのメッセージ送信はエラー"""
        mock_message_service = AsyncMock()
        mock_message_service.send_message.side_effect = ValueError(
            "自分自身にメッセージを送信できません"
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages",
                json={"recipient_id": "test_user_1", "content": "test"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_message_to_non_friend_error(self, client, sample_user2):
        """フレンドでないユーザーへのメッセージ送信はエラー"""
        mock_message_service = AsyncMock()
        mock_message_service.send_message.side_effect = ValueError(
            "メッセージを送信するにはフレンドである必要があります"
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages",
                json={"recipient_id": sample_user2.uid, "content": "test"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_message_insufficient_trust_level_error(self, client, sample_user2):
        """信頼レベル不足のエラー"""
        mock_message_service = AsyncMock()
        mock_message_service.send_message.side_effect = ValueError(
            "メッセージを送信するには信頼レベル2（友達）以上が必要です"
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages",
                json={"recipient_id": sample_user2.uid, "content": "test"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_conversations(self, client, sample_user1, sample_user2):
        """会話一覧取得"""
        mock_message_service = AsyncMock()
        mock_message_service.get_conversations.return_value = [
            AsyncMock(
                conversation_id=f"{sample_user1.uid}_{sample_user2.uid}",
                participant_id=sample_user2.uid,
                last_message_at=datetime.utcnow(),
                last_message_content="最後のメッセージ",
                last_message_sender_id=sample_user2.uid,
                unread_count=3,
                created_at=datetime.utcnow(),
                participant_display_name=sample_user2.display_name,
                participant_profile_image_url=None,
            )
        ]

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.get("/api/v1/messages/conversations")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "conversations" in data
            assert "total" in data
            assert data["total"] == 1
            assert data["conversations"][0]["unread_count"] == 3

    def test_get_conversation_messages(self, client, sample_user1, sample_user2):
        """会話のメッセージ一覧取得"""
        mock_message_service = AsyncMock()
        mock_message_service.get_conversation_messages.return_value = [
            AsyncMock(
                message_id="msg_1",
                conversation_id=f"{sample_user1.uid}_{sample_user2.uid}",
                sender_id=sample_user2.uid,
                recipient_id=sample_user1.uid,
                content="メッセージ1",
                content_type=MessageContentType.TEXT,
                is_visible_to_recipient=True,
                is_read=True,
                created_at=datetime.utcnow(),
                read_at=datetime.utcnow(),
                revealed_at=datetime.utcnow(),
                sender_display_name=sample_user2.display_name,
                sender_profile_image_url=None,
            ),
            AsyncMock(
                message_id="msg_2",
                conversation_id=f"{sample_user1.uid}_{sample_user2.uid}",
                sender_id=sample_user1.uid,
                recipient_id=sample_user2.uid,
                content="メッセージ2",
                content_type=MessageContentType.TEXT,
                is_visible_to_recipient=True,
                is_read=False,
                created_at=datetime.utcnow(),
                read_at=None,
                revealed_at=datetime.utcnow(),
                sender_display_name=sample_user1.display_name,
                sender_profile_image_url=None,
            ),
        ]

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.get(f"/api/v1/messages/conversations/{sample_user2.uid}/messages")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "messages" in data
            assert "total" in data
            assert "has_more" in data
            assert data["total"] == 2
            assert data["messages"][0]["message_id"] == "msg_1"
            assert data["messages"][1]["message_id"] == "msg_2"

    def test_get_conversation_messages_with_pagination(self, client, sample_user2):
        """会話のメッセージ一覧取得（ページネーション）"""
        mock_message_service = AsyncMock()
        mock_message_service.get_conversation_messages.return_value = [
            AsyncMock(
                message_id=f"msg_{i}",
                conversation_id="conv_123",
                sender_id=sample_user2.uid,
                recipient_id="test_user_1",
                content=f"メッセージ{i}",
                content_type=MessageContentType.TEXT,
                is_visible_to_recipient=True,
                is_read=False,
                created_at=datetime.utcnow(),
                read_at=None,
                revealed_at=None,
                sender_display_name=sample_user2.display_name,
                sender_profile_image_url=None,
            )
            for i in range(50)
        ]

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.get(
                f"/api/v1/messages/conversations/{sample_user2.uid}/messages"
                "?limit=50&before_message_id=msg_100"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 50
            assert data["has_more"] is True  # limitと同じ数なのでさらにある可能性

    def test_reveal_messages(self, client):
        """メッセージ表示エンドポイント"""
        mock_message_service = AsyncMock()
        mock_message_service.reveal_messages.return_value = 3

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages/reveal",
                json={"message_ids": ["msg_1", "msg_2", "msg_3"]},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["count"] == 3
            assert "メッセージを表示しました" in data["message"]

    def test_reveal_messages_permission_error(self, client):
        """メッセージ表示時の権限エラー"""
        mock_message_service = AsyncMock()
        mock_message_service.reveal_messages.side_effect = ValueError(
            "このメッセージを表示する権限がありません"
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages/reveal",
                json={"message_ids": ["msg_1"]},
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_mark_messages_as_read(self, client):
        """メッセージ既読エンドポイント"""
        mock_message_service = AsyncMock()
        mock_message_service.mark_messages_as_read.return_value = 2

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages/read",
                json={"message_ids": ["msg_1", "msg_2"]},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["count"] == 2
            assert "既読にしました" in data["message"]

    def test_mark_messages_as_read_permission_error(self, client):
        """メッセージ既読時の権限エラー"""
        mock_message_service = AsyncMock()
        mock_message_service.mark_messages_as_read.side_effect = ValueError(
            "このメッセージを既読にする権限がありません"
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.post(
                "/api/v1/messages/read",
                json={"message_ids": ["msg_1"]},
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_message(self, client):
        """メッセージ削除エンドポイント"""
        mock_message_service = AsyncMock()
        mock_message_service.delete_message.return_value = None

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.delete("/api/v1/messages/msg_123")

            assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_message_not_found(self, client):
        """存在しないメッセージ削除はエラー"""
        mock_message_service = AsyncMock()
        mock_message_service.delete_message.side_effect = ValueError("メッセージが見つかりません")

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.delete("/api/v1/messages/nonexistent_message")

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_message_permission_error(self, client):
        """他人のメッセージ削除はエラー"""
        mock_message_service = AsyncMock()
        mock_message_service.delete_message.side_effect = ValueError(
            "このメッセージを削除する権限がありません"
        )

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.delete("/api/v1/messages/msg_123")

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_unread_count(self, client):
        """未読メッセージ総数取得"""
        mock_message_service = AsyncMock()
        mock_message_service.get_unread_message_count.return_value = 5

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.get("/api/v1/messages/unread-count")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["unread_count"] == 5

    def test_get_unread_count_zero(self, client):
        """未読メッセージがない場合"""
        mock_message_service = AsyncMock()
        mock_message_service.get_unread_message_count.return_value = 0

        with patch("app.api.v1.messages.MessageService", return_value=mock_message_service):
            response = client.get("/api/v1/messages/unread-count")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["unread_count"] == 0
