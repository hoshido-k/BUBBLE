"""
住所・位置情報関連のスキーマ
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AddressType(str, Enum):
    """住所タイプ"""
    HOME = "home"
    WORK = "work"  # 職場（社会人）
    SCHOOL = "school"  # 学校（学生）


class AddressUpdateRequest(BaseModel):
    """住所更新リクエスト"""
    latitude: float = Field(..., ge=-90, le=90, description="緯度")
    longitude: float = Field(..., ge=-180, le=180, description="経度")


class SpecialAddressChangeReason(str, Enum):
    """特別な住所変更理由"""
    MOVING = "moving"  # 引っ越し
    JOB_CHANGE = "job_change"  # 転職
    OTHER = "other"  # その他


class SpecialAddressChangeRequest(BaseModel):
    """特別な住所変更申請"""
    address_type: AddressType
    new_latitude: float = Field(..., ge=-90, le=90)
    new_longitude: float = Field(..., ge=-180, le=180)
    reason: SpecialAddressChangeReason
    description: Optional[str] = Field(None, max_length=500, description="詳細説明")
    document_url: Optional[str] = Field(None, description="証明書類のURL")


class AddressChangeStatus(str, Enum):
    """住所変更申請ステータス"""
    PENDING = "pending"  # 審査中
    APPROVED = "approved"  # 承認済み
    REJECTED = "rejected"  # 却下


class AddressChangeRequestResponse(BaseModel):
    """住所変更申請レスポンス"""
    request_id: str
    user_id: str
    address_type: AddressType
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    new_latitude: float
    new_longitude: float
    reason: SpecialAddressChangeReason
    description: Optional[str] = None
    document_url: Optional[str] = None
    status: AddressChangeStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_comment: Optional[str] = None


class CustomLocationCreate(BaseModel):
    """カスタム場所作成"""
    name: str = Field(..., min_length=1, max_length=50)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(default=100, ge=10, le=1000)
    color: str = Field(default="#9C27B0", description="表示色（HEX）")


class CustomLocationUpdate(BaseModel):
    """カスタム場所更新"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    radius_meters: Optional[int] = Field(None, ge=10, le=1000)
    color: Optional[str] = None
