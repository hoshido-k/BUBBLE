"""
メッセージ関連のPydanticスキーマ定義

Firestoreのコレクション構造:

messages コレクション:
{
    "message_id": "auto-generated",
    "conversation_id": "uid1_uid2",  # 小さいuid + "_" + 大きいuid でソート
    "sender_id": "uid1",
    "recipient_id": "uid2",
    "content": "メッセージ本文",
    "content_type": "text",  # text, image, location
    "is_visible_to_recipient": false,  # 受信者が表示を選択したかどうか
    "is_read": false,  # 既読フラグ
    "created_at": "2024-01-01T00:00:00Z",
    "read_at": null,  # 既読日時
    "revealed_at": null  # 受信者が表示した日時
}

conversations コレクション:
{
    "conversation_id": "uid1_uid2",
    "participant_ids": ["uid1", "uid2"],
    "last_message_at": "2024-01-01T00:00:00Z",
    "last_message_content": "最後のメッセージ...",
    "last_message_sender_id": "uid1",
    "unread_counts": {
        "uid1": 0,
        "uid2": 3
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}

BUBBLEのメッセージ可視性制御:
- メッセージは送信されても、受信者が「表示」を選択するまで非表示
- is_visible_to_recipient=falseの間は、通知だけが届く
- 受信者が「メッセージを表示」を選択すると、revealed_atが記録される
- その後、メッセージを開くとis_read=trueになり、read_atが記録される
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageContentType(str, Enum):
    """メッセージコンテンツタイプ"""

    TEXT = "text"
    IMAGE = "image"
    LOCATION = "location"


class MessageCreate(BaseModel):
    """メッセージ送信"""

    recipient_id: str = Field(..., description="受信者のユーザーID")
    content: str = Field(..., min_length=1, max_length=5000, description="メッセージ本文")
    content_type: MessageContentType = Field(
        default=MessageContentType.TEXT, description="コンテンツタイプ"
    )


class MessageInDB(BaseModel):
    """データベース内のメッセージ"""

    message_id: str
    conversation_id: str
    sender_id: str
    recipient_id: str
    content: str
    content_type: MessageContentType = MessageContentType.TEXT
    is_visible_to_recipient: bool = Field(
        default=False, description="受信者が表示を選択したかどうか"
    )
    is_read: bool = Field(default=False, description="既読フラグ")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(None, description="既読日時")
    revealed_at: Optional[datetime] = Field(None, description="受信者が表示した日時")

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """メッセージのレスポンス"""

    message_id: str
    conversation_id: str
    sender_id: str
    recipient_id: str
    content: str
    content_type: MessageContentType
    is_visible_to_recipient: bool
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    revealed_at: Optional[datetime] = None

    # 送信者の情報（JOIN用）
    sender_display_name: Optional[str] = None
    sender_profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """メッセージ一覧のレスポンス"""

    messages: list[MessageResponse]
    total: int
    has_more: bool = Field(default=False, description="さらにメッセージがあるか")


class ConversationInDB(BaseModel):
    """データベース内の会話"""

    conversation_id: str
    participant_ids: list[str] = Field(..., min_length=2, max_length=2)
    last_message_at: datetime
    last_message_content: str
    last_message_sender_id: str
    unread_counts: dict[str, int] = Field(
        default_factory=dict, description="各ユーザーの未読数"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """会話のレスポンス"""

    conversation_id: str
    participant_id: str  # 会話相手のID
    last_message_at: datetime
    last_message_content: str
    last_message_sender_id: str
    unread_count: int = Field(default=0, description="未読メッセージ数")
    created_at: datetime

    # 会話相手の情報（JOIN用）
    participant_display_name: Optional[str] = None
    participant_profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """会話一覧のレスポンス"""

    conversations: list[ConversationResponse]
    total: int


class MessageRevealRequest(BaseModel):
    """メッセージ表示リクエスト（受信者が表示を選択）"""

    message_ids: list[str] = Field(..., min_length=1, description="表示するメッセージIDのリスト")


class MessageMarkReadRequest(BaseModel):
    """メッセージ既読リクエスト"""

    message_ids: list[str] = Field(..., min_length=1, description="既読にするメッセージIDのリスト")
