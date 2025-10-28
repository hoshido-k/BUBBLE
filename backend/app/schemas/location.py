"""
位置情報ステータス関連のスキーマ
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LocationStatus(str, Enum):
    """位置情報ステータス"""
    HOME = "home"  # 🏠 自宅
    WORK = "work"  # 🏢 職場（社会人）
    SCHOOL = "school"  # 🏫 学校（学生）
    MOVING = "moving"  # 🚶 移動中
    CUSTOM = "custom"  # 📍 カスタム場所
    UNKNOWN = "unknown"  # ❓ 不明


class LocationUpdateRequest(BaseModel):
    """位置情報更新リクエスト"""
    latitude: float = Field(..., ge=-90, le=90, description="緯度")
    longitude: float = Field(..., ge=-180, le=180, description="経度")
    accuracy: Optional[float] = Field(None, ge=0, description="精度（メートル）")
    speed: Optional[float] = Field(None, ge=0, description="速度（m/s）")


class LocationResponse(BaseModel):
    """位置情報レスポンス"""
    user_id: str
    status: LocationStatus
    last_updated: datetime
    custom_location_name: Optional[str] = Field(None, description="カスタム場所名")


class LocationHistoryItem(BaseModel):
    """位置履歴アイテム"""
    timestamp: datetime
    status: LocationStatus
    custom_location_name: Optional[str] = None


class LocationHistoryResponse(BaseModel):
    """位置履歴レスポンス"""
    user_id: str
    history: list[LocationHistoryItem]
    retention_days: int = Field(description="保持日数")


class CurrentLocationResponse(BaseModel):
    """現在の位置情報詳細レスポンス"""
    user_id: str
    status: LocationStatus
    status_display: str = Field(description="表示用ステータス文字列")
    color: str = Field(description="ステータス表示色（HEX）")
    last_updated: datetime
    custom_location_name: Optional[str] = None
    is_home_registered: bool = Field(description="自宅が登録されているか")
    is_work_registered: bool = Field(description="職場が登録されているか")
    is_school_registered: bool = Field(description="学校が登録されているか")


class CustomLocationResponse(BaseModel):
    """カスタム場所レスポンス"""
    location_id: str
    user_id: str
    name: str
    latitude: float
    longitude: float
    radius_meters: int
    color: str
    created_at: datetime
    updated_at: datetime


class NearMissNotification(BaseModel):
    """ニアミス通知"""
    notification_id: str
    friend_user_id: str
    friend_name: str
    detected_at: datetime
    location_status: LocationStatus
    distance_meters: Optional[int] = Field(None, description="おおよその距離")
    time_difference_minutes: int = Field(description="時間差（分）")
