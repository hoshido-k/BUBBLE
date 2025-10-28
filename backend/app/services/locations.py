"""
位置情報サービス
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from google.cloud.firestore_v1 import FieldFilter

from app.config import settings
from app.core.firebase import get_firestore_client
from app.schemas.location import (
    CurrentLocationResponse,
    LocationHistoryItem,
    LocationHistoryResponse,
    LocationResponse,
    LocationStatus,
    LocationUpdateRequest,
)
from app.utils.encryption import encrypt_location_data


class LocationService:
    """位置情報サービスクラス"""

    def __init__(self):
        self.db = get_firestore_client()

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        2点間の距離を計算（ハバーサイン式）

        Args:
            lat1: 地点1の緯度
            lon1: 地点1の経度
            lat2: 地点2の緯度
            lon2: 地点2の経度

        Returns:
            float: 距離（メートル）
        """
        # 地球の半径（メートル）
        R = 6371000

        # ラジアンに変換
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # ハバーサイン式
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    async def determine_location_status(
        self, user_id: str, latitude: float, longitude: float, speed: Optional[float] = None
    ) -> tuple[LocationStatus, Optional[str]]:
        """
        位置情報から現在のステータスを判定

        Args:
            user_id: ユーザーID
            latitude: 緯度
            longitude: 経度
            speed: 速度（m/s）

        Returns:
            tuple[LocationStatus, Optional[str]]: (ステータス, カスタム場所名)
        """
        # ユーザー情報を取得
        user_ref = self.db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return LocationStatus.UNKNOWN, None

        user_data = user_doc.to_dict()

        # 自宅の確認
        if "home_address" in user_data and user_data["home_address"]:
            home_addr = user_data["home_address"]
            if "latitude" in home_addr and "longitude" in home_addr:
                home_distance = self.calculate_distance(
                    latitude, longitude, home_addr["latitude"], home_addr["longitude"]
                )
                if home_distance <= settings.HOME_RADIUS_METERS:
                    return LocationStatus.HOME, None

        # 職場の確認（社会人の場合）
        if "work_address" in user_data and user_data["work_address"]:
            work_addr = user_data["work_address"]
            if "latitude" in work_addr and "longitude" in work_addr:
                work_distance = self.calculate_distance(
                    latitude, longitude, work_addr["latitude"], work_addr["longitude"]
                )
                if work_distance <= settings.WORK_RADIUS_METERS:
                    return LocationStatus.WORK, None

        # 学校の確認（学生の場合）
        if "school_address" in user_data and user_data["school_address"]:
            school_addr = user_data["school_address"]
            if "latitude" in school_addr and "longitude" in school_addr:
                school_distance = self.calculate_distance(
                    latitude, longitude, school_addr["latitude"], school_addr["longitude"]
                )
                if school_distance <= settings.SCHOOL_RADIUS_METERS:
                    return LocationStatus.SCHOOL, None

        # カスタム場所の確認
        custom_locations = user_data.get("custom_locations", [])
        for custom_loc in custom_locations:
            custom_distance = self.calculate_distance(
                latitude, longitude, custom_loc["latitude"], custom_loc["longitude"]
            )
            if custom_distance <= custom_loc.get("radius_meters", 100):
                return LocationStatus.CUSTOM, custom_loc.get("name")

        # 移動中の判定（速度が5km/h以上）
        if speed is not None and speed > 1.4:  # 5km/h = 約1.4m/s
            return LocationStatus.MOVING, None

        # それ以外は不明
        return LocationStatus.UNKNOWN, None

    async def update_location(self, user_id: str, location_data: LocationUpdateRequest) -> LocationResponse:
        """
        位置情報を更新

        Args:
            user_id: ユーザーID
            location_data: 位置情報データ

        Returns:
            LocationResponse: 更新後の位置情報
        """
        now = datetime.now(timezone.utc)

        # ステータスを判定
        status, custom_location_name = await self.determine_location_status(
            user_id, location_data.latitude, location_data.longitude, location_data.speed
        )

        # 位置情報を暗号化
        encrypted_data = encrypt_location_data(
            location_data.latitude,
            location_data.longitude,
            accuracy=location_data.accuracy,
            speed=location_data.speed,
            timestamp=now.isoformat(),
        )

        # 現在の位置情報を更新
        location_ref = self.db.collection("user_locations").document(user_id)
        location_ref.set(
            {
                "user_id": user_id,
                "status": status.value,
                "custom_location_name": custom_location_name,
                "encrypted_data": encrypted_data,
                "last_updated": now,
            }
        )

        # 位置履歴に追加
        history_ref = self.db.collection("location_history").document()
        history_ref.set(
            {
                "user_id": user_id,
                "status": status.value,
                "custom_location_name": custom_location_name,
                "encrypted_data": encrypted_data,
                "timestamp": now,
            }
        )

        # 古い履歴を削除（7日以上前）
        retention_date = now - timedelta(days=settings.LOCATION_HISTORY_RETENTION_DAYS)
        old_history = (
            self.db.collection("location_history")
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("timestamp", "<", retention_date))
        )
        old_docs = old_history.get()
        for doc in old_docs:
            doc.reference.delete()

        return LocationResponse(
            user_id=user_id, status=status, last_updated=now, custom_location_name=custom_location_name
        )

    async def get_current_location(self, user_id: str) -> Optional[CurrentLocationResponse]:
        """
        現在の位置情報を取得

        Args:
            user_id: ユーザーID

        Returns:
            Optional[CurrentLocationResponse]: 位置情報（存在しない場合はNone）
        """
        # 現在の位置情報を取得
        location_ref = self.db.collection("user_locations").document(user_id)
        location_doc = location_ref.get()

        if not location_doc.exists:
            return None

        location_data = location_doc.to_dict()
        status = LocationStatus(location_data["status"])

        # ユーザー情報を取得（登録済み住所の確認）
        user_ref = self.db.collection("users").document(user_id)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict() if user_doc.exists else {}

        # ステータス表示文字列と色を決定
        status_display_map = {
            LocationStatus.HOME: ("🏠 自宅", "#4CAF50"),
            LocationStatus.WORK: ("🏢 職場", "#2196F3"),
            LocationStatus.SCHOOL: ("🏫 学校", "#FF9800"),
            LocationStatus.MOVING: ("🚶 移動中", "#FFC107"),
            LocationStatus.CUSTOM: (f"📍 {location_data.get('custom_location_name', 'カスタム')}", "#9C27B0"),
            LocationStatus.UNKNOWN: ("❓ 不明", "#9E9E9E"),
        }

        status_display, color = status_display_map.get(status, ("不明", "#9E9E9E"))

        return CurrentLocationResponse(
            user_id=user_id,
            status=status,
            status_display=status_display,
            color=color,
            last_updated=location_data["last_updated"],
            custom_location_name=location_data.get("custom_location_name"),
            is_home_registered=bool(user_data.get("home_address")),
            is_work_registered=bool(user_data.get("work_address")),
            is_school_registered=bool(user_data.get("school_address")),
        )

    async def get_location_history(self, user_id: str, days: int = 7) -> LocationHistoryResponse:
        """
        位置履歴を取得

        Args:
            user_id: ユーザーID
            days: 取得する日数（デフォルト7日）

        Returns:
            LocationHistoryResponse: 位置履歴
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        history_ref = (
            self.db.collection("location_history")
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("timestamp", ">=", start_date))
            .order_by("timestamp", direction="DESCENDING")
        )

        history_docs = history_ref.get()

        history_items = []
        for doc in history_docs:
            data = doc.to_dict()
            history_items.append(
                LocationHistoryItem(
                    timestamp=data["timestamp"],
                    status=LocationStatus(data["status"]),
                    custom_location_name=data.get("custom_location_name"),
                )
            )

        return LocationHistoryResponse(user_id=user_id, history=history_items, retention_days=days)

    async def get_friend_location(self, user_id: str, friend_id: str) -> Optional[CurrentLocationResponse]:
        """
        フレンドの現在位置を取得（フレンド関係のチェック付き）

        Args:
            user_id: リクエストユーザーID
            friend_id: フレンドのユーザーID

        Returns:
            Optional[CurrentLocationResponse]: フレンドの位置情報

        Raises:
            ValueError: フレンド関係がない場合
        """
        # フレンド関係を確認
        friend_ref = (
            self.db.collection("friendships")
            .where(filter=FieldFilter("user_id", "==", user_id))
            .where(filter=FieldFilter("friend_id", "==", friend_id))
            .where(filter=FieldFilter("status", "==", "accepted"))
        )
        friend_doc = friend_ref.get()

        if not friend_doc:
            raise ValueError("フレンド関係がありません")

        # フレンドの位置情報を取得
        return await self.get_current_location(friend_id)
