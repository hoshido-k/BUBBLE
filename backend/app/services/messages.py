"""
メッセージングサービス
"""

from datetime import datetime
from typing import List, Optional

from google.cloud.firestore_v1 import FieldFilter

from app.core.firebase import get_firestore_client
from app.schemas.friend import TrustLevel
from app.schemas.message import (
    ConversationInDB,
    ConversationResponse,
    MessageCreate,
    MessageInDB,
    MessageResponse,
)
from app.services.friends import FriendService
from app.services.users import UserService


class MessageService:
    """メッセージングサービスクラス"""

    def __init__(self):
        self.db = get_firestore_client()
        self.user_service = UserService()
        self.friend_service = FriendService()

    def _get_conversation_id(self, user_id1: str, user_id2: str) -> str:
        """
        会話IDを生成（ユーザーIDをソートして結合）

        Args:
            user_id1: ユーザーID1
            user_id2: ユーザーID2

        Returns:
            会話ID
        """
        sorted_ids = sorted([user_id1, user_id2])
        return f"{sorted_ids[0]}_{sorted_ids[1]}"

    async def _check_messaging_permission(self, sender_id: str, recipient_id: str) -> bool:
        """
        メッセージ送信権限をチェック（信頼レベル2以上が必要）

        Args:
            sender_id: 送信者ID
            recipient_id: 受信者ID

        Returns:
            メッセージ送信可能な場合True

        Raises:
            ValueError: フレンドでない、または信頼レベルが不足している場合
        """
        trust_level = await self.friend_service.get_trust_level(sender_id, recipient_id)

        if trust_level is None:
            raise ValueError("メッセージを送信するにはフレンドである必要があります")

        if trust_level.value < TrustLevel.FRIEND.value:
            raise ValueError("メッセージを送信するには信頼レベル2（友達）以上が必要です")

        return True

    async def send_message(self, sender_id: str, message_data: MessageCreate) -> MessageResponse:
        """
        メッセージを送信

        Args:
            sender_id: 送信者ID
            message_data: メッセージデータ

        Returns:
            送信されたメッセージ

        Raises:
            ValueError: フレンドでない、信頼レベル不足、受信者が存在しない場合
        """
        recipient_id = message_data.recipient_id

        # 自分自身へのメッセージはエラー
        if sender_id == recipient_id:
            raise ValueError("自分自身にメッセージを送信できません")

        # 受信者が存在するか確認
        recipient = await self.user_service.get_user_by_uid(recipient_id)
        if not recipient:
            raise ValueError("指定された受信者が見つかりません")

        # メッセージ送信権限をチェック
        await self._check_messaging_permission(sender_id, recipient_id)

        # 会話IDを生成
        conversation_id = self._get_conversation_id(sender_id, recipient_id)

        # メッセージを作成
        message_ref = self.db.collection("messages").document()
        message_dict = {
            "message_id": message_ref.id,
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": message_data.content,
            "content_type": message_data.content_type.value,
            "is_visible_to_recipient": False,  # デフォルトでは非表示
            "is_read": False,
            "created_at": datetime.utcnow(),
            "read_at": None,
            "revealed_at": None,
        }

        message_ref.set(message_dict)

        # 会話を作成/更新
        await self._create_or_update_conversation(
            conversation_id=conversation_id,
            participant_ids=[sender_id, recipient_id],
            last_message_content=message_data.content,
            last_message_sender_id=sender_id,
            recipient_id=recipient_id,
        )

        # 送信者の情報を取得して返す
        sender = await self.user_service.get_user_by_uid(sender_id)
        message_dict["sender_display_name"] = sender.display_name if sender else None
        message_dict["sender_profile_image_url"] = sender.profile_image_url if sender else None

        return MessageResponse(**message_dict)

    async def _create_or_update_conversation(
        self,
        conversation_id: str,
        participant_ids: List[str],
        last_message_content: str,
        last_message_sender_id: str,
        recipient_id: str,
    ) -> None:
        """
        会話を作成または更新（内部メソッド）

        Args:
            conversation_id: 会話ID
            participant_ids: 参加者IDリスト
            last_message_content: 最後のメッセージ内容
            last_message_sender_id: 最後のメッセージ送信者ID
            recipient_id: 受信者ID（未読数をインクリメント）
        """
        conversation_ref = self.db.collection("conversations").document(conversation_id)
        conversation_doc = conversation_ref.get()

        now = datetime.utcnow()

        if not conversation_doc.exists:
            # 新規会話を作成
            conversation_data = {
                "conversation_id": conversation_id,
                "participant_ids": participant_ids,
                "last_message_at": now,
                "last_message_content": last_message_content,
                "last_message_sender_id": last_message_sender_id,
                "unread_counts": {participant_ids[0]: 0, participant_ids[1]: 0},
                "created_at": now,
                "updated_at": now,
            }
            # 受信者の未読数を1にする
            conversation_data["unread_counts"][recipient_id] = 1
            conversation_ref.set(conversation_data)
        else:
            # 既存の会話を更新
            conversation_data = conversation_doc.to_dict()
            unread_counts = conversation_data.get("unread_counts", {})

            # 受信者の未読数をインクリメント
            unread_counts[recipient_id] = unread_counts.get(recipient_id, 0) + 1

            conversation_ref.update(
                {
                    "last_message_at": now,
                    "last_message_content": last_message_content,
                    "last_message_sender_id": last_message_sender_id,
                    "unread_counts": unread_counts,
                    "updated_at": now,
                }
            )

    async def get_conversation_messages(
        self,
        user_id: str,
        other_user_id: str,
        limit: int = 50,
        before_message_id: Optional[str] = None,
    ) -> List[MessageResponse]:
        """
        会話のメッセージ一覧を取得

        Args:
            user_id: 現在のユーザーID
            other_user_id: 会話相手のユーザーID
            limit: 取得件数（デフォルト50件）
            before_message_id: このメッセージIDより前のメッセージを取得（ページネーション用）

        Returns:
            メッセージ一覧

        Raises:
            ValueError: フレンドでない、信頼レベル不足の場合
        """
        # メッセージ閲覧権限をチェック
        await self._check_messaging_permission(user_id, other_user_id)

        conversation_id = self._get_conversation_id(user_id, other_user_id)

        # メッセージを取得
        query = (
            self.db.collection("messages")
            .where(filter=FieldFilter("conversation_id", "==", conversation_id))
            .order_by("created_at", direction="DESCENDING")
        )

        # ページネーション
        if before_message_id:
            before_message_ref = self.db.collection("messages").document(before_message_id)
            before_message_doc = before_message_ref.get()
            if before_message_doc.exists:
                query = query.start_after(before_message_doc)

        query = query.limit(limit)
        messages = query.get()

        result = []
        for msg in messages:
            msg_data = msg.to_dict()

            # 送信者の情報を取得
            sender = await self.user_service.get_user_by_uid(msg_data["sender_id"])
            if sender:
                msg_data["sender_display_name"] = sender.display_name
                msg_data["sender_profile_image_url"] = sender.profile_image_url

            # 自分が受信者の場合、is_visible_to_recipient=falseのメッセージはフィルタリング
            if msg_data["recipient_id"] == user_id and not msg_data.get(
                "is_visible_to_recipient", False
            ):
                continue

            result.append(MessageResponse(**msg_data))

        # 新しい順→古い順に並び替え（UIで表示しやすいように）
        result.reverse()

        return result

    async def get_conversations(self, user_id: str) -> List[ConversationResponse]:
        """
        会話一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            会話一覧
        """
        conversations = (
            self.db.collection("conversations")
            .where(filter=FieldFilter("participant_ids", "array_contains", user_id))
            .order_by("last_message_at", direction="DESCENDING")
            .get()
        )

        result = []
        for conv in conversations:
            conv_data = conv.to_dict()

            # 会話相手のIDを取得
            participant_ids = conv_data["participant_ids"]
            other_user_id = (
                participant_ids[0] if participant_ids[0] != user_id else participant_ids[1]
            )

            # 会話相手の情報を取得
            other_user = await self.user_service.get_user_by_uid(other_user_id)
            if not other_user:
                continue

            # 自分の未読数を取得
            unread_counts = conv_data.get("unread_counts", {})
            my_unread_count = unread_counts.get(user_id, 0)

            conversation_response = ConversationResponse(
                conversation_id=conv_data["conversation_id"],
                participant_id=other_user_id,
                last_message_at=conv_data["last_message_at"],
                last_message_content=conv_data["last_message_content"],
                last_message_sender_id=conv_data["last_message_sender_id"],
                unread_count=my_unread_count,
                created_at=conv_data["created_at"],
                participant_display_name=other_user.display_name,
                participant_profile_image_url=other_user.profile_image_url,
            )

            result.append(conversation_response)

        return result

    async def reveal_messages(self, user_id: str, message_ids: List[str]) -> int:
        """
        メッセージを表示（受信者が表示を選択）

        Args:
            user_id: 現在のユーザーID（受信者）
            message_ids: 表示するメッセージIDリスト

        Returns:
            更新されたメッセージ数

        Raises:
            ValueError: 権限がない場合
        """
        updated_count = 0
        now = datetime.utcnow()

        for message_id in message_ids:
            message_ref = self.db.collection("messages").document(message_id)
            message_doc = message_ref.get()

            if not message_doc.exists:
                continue

            message_data = message_doc.to_dict()

            # 受信者かチェック
            if message_data["recipient_id"] != user_id:
                raise ValueError("このメッセージを表示する権限がありません")

            # 既に表示済みの場合はスキップ
            if message_data.get("is_visible_to_recipient", False):
                continue

            # メッセージを表示
            message_ref.update({"is_visible_to_recipient": True, "revealed_at": now})
            updated_count += 1

        return updated_count

    async def mark_messages_as_read(self, user_id: str, message_ids: List[str]) -> int:
        """
        メッセージを既読にする

        Args:
            user_id: 現在のユーザーID（受信者）
            message_ids: 既読にするメッセージIDリスト

        Returns:
            更新されたメッセージ数

        Raises:
            ValueError: 権限がない場合
        """
        updated_count = 0
        now = datetime.utcnow()

        # 会話ごとの未読数を減らすためのカウンター
        conversation_unread_decrements: dict[str, int] = {}

        for message_id in message_ids:
            message_ref = self.db.collection("messages").document(message_id)
            message_doc = message_ref.get()

            if not message_doc.exists:
                continue

            message_data = message_doc.to_dict()

            # 受信者かチェック
            if message_data["recipient_id"] != user_id:
                raise ValueError("このメッセージを既読にする権限がありません")

            # 既に既読の場合はスキップ
            if message_data.get("is_read", False):
                continue

            # メッセージを既読にする
            message_ref.update({"is_read": True, "read_at": now})
            updated_count += 1

            # 会話の未読数を減らす準備
            conversation_id = message_data["conversation_id"]
            conversation_unread_decrements[conversation_id] = (
                conversation_unread_decrements.get(conversation_id, 0) + 1
            )

        # 会話の未読数を更新
        for conversation_id, decrement in conversation_unread_decrements.items():
            conversation_ref = self.db.collection("conversations").document(conversation_id)
            conversation_doc = conversation_ref.get()

            if conversation_doc.exists:
                conversation_data = conversation_doc.to_dict()
                unread_counts = conversation_data.get("unread_counts", {})
                current_unread = unread_counts.get(user_id, 0)
                new_unread = max(0, current_unread - decrement)
                unread_counts[user_id] = new_unread

                conversation_ref.update({"unread_counts": unread_counts})

        return updated_count

    async def delete_message(self, user_id: str, message_id: str) -> None:
        """
        メッセージを削除

        Args:
            user_id: 現在のユーザーID
            message_id: 削除するメッセージID

        Raises:
            ValueError: メッセージが見つからない、権限がない場合
        """
        message_ref = self.db.collection("messages").document(message_id)
        message_doc = message_ref.get()

        if not message_doc.exists:
            raise ValueError("メッセージが見つかりません")

        message_data = message_doc.to_dict()

        # 送信者のみが削除可能
        if message_data["sender_id"] != user_id:
            raise ValueError("このメッセージを削除する権限がありません")

        # メッセージを削除
        message_ref.delete()

    async def get_unread_message_count(self, user_id: str) -> int:
        """
        未読メッセージの総数を取得

        Args:
            user_id: ユーザーID

        Returns:
            未読メッセージ総数
        """
        conversations = (
            self.db.collection("conversations")
            .where(filter=FieldFilter("participant_ids", "array_contains", user_id))
            .get()
        )

        total_unread = 0
        for conv in conversations:
            conv_data = conv.to_dict()
            unread_counts = conv_data.get("unread_counts", {})
            total_unread += unread_counts.get(user_id, 0)

        return total_unread
