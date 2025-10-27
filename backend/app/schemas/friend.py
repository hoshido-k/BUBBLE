"""
フレンド関連のPydanticスキーマ定義

Firestoreのコレクション構造:

friendships コレクション:
{
    "friendship_id": "auto-generated",
    "user_id": "uid1",  # フレンド関係の一方のユーザー
    "friend_id": "uid2",  # フレンド関係のもう一方のユーザー
    "trust_level": 3,  # 1-5の信頼レベル (5が最も信頼度が高い)
    "nickname": "親友の太郎",  # オプション：ニックネーム
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "status": "active"  # active, blocked
}

friend_requests コレクション:
{
    "request_id": "auto-generated",
    "from_user_id": "uid1",  # リクエスト送信者
    "to_user_id": "uid2",  # リクエスト受信者
    "message": "よろしくお願いします",  # オプション
    "status": "pending",  # pending, accepted, rejected
    "created_at": "2024-01-01T00:00:00Z",
    "responded_at": "2024-01-01T00:00:00Z"  # 承認/拒否された日時
}

信頼レベル:
- Level 1: 知り合い (位置ステータスのみ共有)
- Level 2: 友達 (メッセージ可能)
- Level 3: 仲良し (過去の位置履歴も共有)
- Level 4: 親しい友達 (カスタム場所も共有)
- Level 5: 最も親しい友達 (near-miss検出有効、住所変更通知)
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FriendRequestStatus(str, Enum):
    """フレンドリクエストのステータス"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FriendshipStatus(str, Enum):
    """フレンド関係のステータス"""

    ACTIVE = "active"
    BLOCKED = "blocked"


class TrustLevel(int, Enum):
    """信頼レベル (1-5)"""

    ACQUAINTANCE = 1  # 知り合い
    FRIEND = 2  # 友達
    GOOD_FRIEND = 3  # 仲良し
    CLOSE_FRIEND = 4  # 親しい友達
    BEST_FRIEND = 5  # 最も親しい友達


class FriendRequestCreate(BaseModel):
    """フレンドリクエスト送信"""

    to_user_id: str = Field(..., description="リクエスト送信先のユーザーID")
    message: Optional[str] = Field(None, max_length=200, description="メッセージ")


class FriendRequestResponse(BaseModel):
    """フレンドリクエストのレスポンス"""

    request_id: str
    from_user_id: str
    to_user_id: str
    message: Optional[str] = None
    status: FriendRequestStatus
    created_at: datetime
    responded_at: Optional[datetime] = None

    # リクエスト送信者の情報（JOIN用）
    from_user_display_name: Optional[str] = None
    from_user_profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FriendRequestAcceptReject(BaseModel):
    """フレンドリクエスト承認/拒否"""

    request_id: str = Field(..., description="リクエストID")


class FriendshipBase(BaseModel):
    """フレンド関係の基本情報"""

    user_id: str
    friend_id: str
    trust_level: TrustLevel = Field(default=TrustLevel.FRIEND, ge=1, le=5)
    nickname: Optional[str] = Field(None, max_length=50, description="フレンドに付けるニックネーム")


class FriendshipInDB(FriendshipBase):
    """データベース内のフレンド関係"""

    friendship_id: str
    status: FriendshipStatus = FriendshipStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class FriendshipResponse(BaseModel):
    """フレンド情報のレスポンス"""

    friendship_id: str
    friend_id: str
    trust_level: TrustLevel
    nickname: Optional[str] = None
    status: FriendshipStatus
    created_at: datetime

    # フレンドのユーザー情報（JOIN用）
    friend_display_name: Optional[str] = None
    friend_email: Optional[str] = None
    friend_profile_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FriendshipUpdate(BaseModel):
    """フレンド関係の更新"""

    trust_level: Optional[TrustLevel] = Field(None, ge=1, le=5, description="信頼レベル")
    nickname: Optional[str] = Field(None, max_length=50, description="ニックネーム")


class FriendListResponse(BaseModel):
    """フレンド一覧のレスポンス"""

    friends: list[FriendshipResponse]
    total: int


class FriendRequestListResponse(BaseModel):
    """フレンドリクエスト一覧のレスポンス"""

    requests: list[FriendRequestResponse]
    total: int
