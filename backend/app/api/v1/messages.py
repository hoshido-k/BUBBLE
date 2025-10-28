"""
メッセージAPIエンドポイント
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencies import get_current_user
from app.schemas.message import (
    ConversationListResponse,
    MessageCreate,
    MessageListResponse,
    MessageMarkReadRequest,
    MessageResponse,
    MessageRevealRequest,
)
from app.schemas.user import UserInDB
from app.services.messages import MessageService

router = APIRouter()


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    メッセージを送信

    フレンド（信頼レベル2以上）にメッセージを送信します。
    送信されたメッセージは受信者が「表示」を選択するまで非表示になります。

    Args:
        message_data: メッセージデータ
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Returns:
        送信されたメッセージ

    Raises:
        HTTPException: フレンドでない、信頼レベル不足、受信者が存在しない場合
    """
    try:
        message = await message_service.send_message(current_user.uid, message_data)
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    会話一覧を取得

    自分が参加している全ての会話（チャットスレッド）の一覧を取得します。
    最新のメッセージ順に並びます。

    Args:
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Returns:
        会話一覧
    """
    conversations = await message_service.get_conversations(current_user.uid)
    return ConversationListResponse(conversations=conversations, total=len(conversations))


@router.get("/conversations/{other_user_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    other_user_id: str = Path(..., description="会話相手のユーザーID"),
    limit: int = Query(50, ge=1, le=100, description="取得件数"),
    before_message_id: Optional[str] = Query(None, description="このメッセージIDより前のメッセージを取得"),
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    会話のメッセージ一覧を取得

    特定の会話相手とのメッセージ履歴を取得します。
    古い順に並びます。

    Args:
        other_user_id: 会話相手のユーザーID
        limit: 取得件数（1-100、デフォルト50）
        before_message_id: ページネーション用のメッセージID
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Returns:
        メッセージ一覧

    Raises:
        HTTPException: フレンドでない、信頼レベル不足の場合
    """
    try:
        messages = await message_service.get_conversation_messages(
            user_id=current_user.uid,
            other_user_id=other_user_id,
            limit=limit,
            before_message_id=before_message_id,
        )

        # さらにメッセージがあるかチェック
        has_more = len(messages) == limit

        return MessageListResponse(messages=messages, total=len(messages), has_more=has_more)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reveal", response_model=dict)
async def reveal_messages(
    reveal_data: MessageRevealRequest,
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    メッセージを表示（受信者が表示を選択）

    BUBBLEの特徴的な機能：受信者が明示的に「表示」を選択するまでメッセージは非表示です。
    このエンドポイントで表示を選択すると、メッセージが閲覧可能になります。

    Args:
        reveal_data: 表示するメッセージIDのリスト
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Returns:
        更新されたメッセージ数

    Raises:
        HTTPException: 権限がない場合
    """
    try:
        updated_count = await message_service.reveal_messages(
            current_user.uid, reveal_data.message_ids
        )
        return {"message": f"{updated_count}件のメッセージを表示しました", "count": updated_count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/read", response_model=dict)
async def mark_messages_as_read(
    read_data: MessageMarkReadRequest,
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    メッセージを既読にする

    指定したメッセージを既読にします。
    既読にすると会話の未読数が減ります。

    Args:
        read_data: 既読にするメッセージIDのリスト
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Returns:
        更新されたメッセージ数

    Raises:
        HTTPException: 権限がない場合
    """
    try:
        updated_count = await message_service.mark_messages_as_read(
            current_user.uid, read_data.message_ids
        )
        return {"message": f"{updated_count}件のメッセージを既読にしました", "count": updated_count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: str = Path(..., description="削除するメッセージID"),
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    メッセージを削除

    自分が送信したメッセージを削除します。
    送信者のみが削除可能です。

    Args:
        message_id: 削除するメッセージID
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Raises:
        HTTPException: メッセージが見つからない、権限がない場合
    """
    try:
        await message_service.delete_message(current_user.uid, message_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: UserInDB = Depends(get_current_user),
    message_service: MessageService = Depends(lambda: MessageService()),
):
    """
    未読メッセージの総数を取得

    全ての会話の未読メッセージ数を合計して返します。

    Args:
        current_user: 現在のユーザー
        message_service: メッセージサービス

    Returns:
        未読メッセージ総数
    """
    unread_count = await message_service.get_unread_message_count(current_user.uid)
    return {"unread_count": unread_count}
