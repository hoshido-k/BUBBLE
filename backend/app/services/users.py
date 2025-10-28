"""
ユーザー管理サービス
"""

from datetime import UTC, datetime, timedelta
from typing import List, Optional

from app.config import settings
from app.core.firebase import get_firestore_client
from app.schemas.address import (
    AddressType,
    AddressUpdateRequest,
    CustomLocationCreate,
    CustomLocationUpdate,
    SpecialAddressChangeRequest,
)
from app.schemas.user import Address, CustomLocation, UserInDB, UserUpdate


class UserService:
    """ユーザー管理サービスクラス"""

    def __init__(self):
        self.db = get_firestore_client()

    async def get_user_by_uid(self, uid: str) -> Optional[UserInDB]:
        """
        UIDからユーザー情報を取得

        Args:
            uid: ユーザーID

        Returns:
            ユーザー情報、存在しない場合はNone
        """
        user_ref = self.db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return None

        user_data = user_doc.to_dict()
        return UserInDB(**user_data)

    async def update_profile(self, uid: str, update_data: UserUpdate) -> UserInDB:
        """
        プロフィール情報を更新

        Args:
            uid: ユーザーID
            update_data: 更新データ

        Returns:
            更新後のユーザー情報

        Raises:
            ValueError: ユーザーが見つからない場合
        """
        user_ref = self.db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise ValueError("ユーザーが見つかりません")

        # 更新データの準備（Noneでない値のみ）
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
        update_dict["updated_at"] = datetime.now(UTC)

        # Firestoreを更新
        user_ref.update(update_dict)

        # 更新後のユーザー情報を取得
        return await self.get_user_by_uid(uid)

    async def can_change_address(self, uid: str, address_type: AddressType) -> bool:
        """
        住所変更が可能かチェック（90日制限）

        Args:
            uid: ユーザーID
            address_type: 住所タイプ（home/work）

        Returns:
            変更可能な場合True
        """
        user = await self.get_user_by_uid(uid)
        if not user:
            return False

        # 該当する住所を取得
        address = user.home_address if address_type == AddressType.HOME else user.work_address

        if not address:
            # 住所が未登録の場合は変更可能
            return True

        # 最後に変更した日時から90日経過しているかチェック
        days_since_change = (datetime.now(UTC) - address.last_changed_at).days
        return days_since_change >= settings.LOCATION_CHANGE_LOCK_DAYS

    async def update_address(
        self, uid: str, address_type: AddressType, address_data: AddressUpdateRequest
    ) -> UserInDB:
        """
        住所を更新（90日制限チェック付き）

        Args:
            uid: ユーザーID
            address_type: 住所タイプ
            address_data: 新しい住所データ

        Returns:
            更新後のユーザー情報

        Raises:
            ValueError: 変更制限期間内の場合
        """
        # 変更可能かチェック
        if not await self.can_change_address(uid, address_type):
            days_left = settings.LOCATION_CHANGE_LOCK_DAYS - (
                datetime.now(UTC)
                - (
                    (await self.get_user_by_uid(uid)).home_address.last_changed_at
                    if address_type == AddressType.HOME
                    else (await self.get_user_by_uid(uid)).work_address.last_changed_at
                )
            ).days
            raise ValueError(f"住所変更は{settings.LOCATION_CHANGE_LOCK_DAYS}日間制限されています。残り{days_left}日です。")

        # 新しい住所オブジェクトを作成
        new_address = Address(
            latitude=address_data.latitude,
            longitude=address_data.longitude,
            registered_at=datetime.now(UTC),
            last_changed_at=datetime.now(UTC),
        )

        # Firestoreを更新
        user_ref = self.db.collection("users").document(uid)
        field_name = "home_address" if address_type == AddressType.HOME else "work_address"

        user_ref.update(
            {field_name: new_address.model_dump(mode="json"), "updated_at": datetime.now(UTC)}
        )

        return await self.get_user_by_uid(uid)

    async def create_special_address_change_request(
        self, uid: str, request: SpecialAddressChangeRequest
    ) -> str:
        """
        特別な住所変更申請を作成

        Args:
            uid: ユーザーID
            request: 変更申請データ

        Returns:
            申請ID

        Raises:
            ValueError: 通常の変更が可能な場合
        """
        # 通常の変更が可能な場合はエラー
        if await self.can_change_address(uid, request.address_type):
            raise ValueError("通常の住所変更が可能です。特別申請は不要です。")

        # 申請をFirestoreに保存
        request_ref = self.db.collection("address_change_requests").document()
        request_data = {
            "request_id": request_ref.id,
            "user_id": uid,
            "address_type": request.address_type.value,
            "new_latitude": request.new_latitude,
            "new_longitude": request.new_longitude,
            "reason": request.reason.value,
            "description": request.description,
            "document_url": request.document_url,
            "status": "pending",
            "created_at": datetime.now(UTC),
            "reviewed_at": None,
            "reviewer_comment": None,
        }

        # 現在の住所も記録
        user = await self.get_user_by_uid(uid)
        if request.address_type == AddressType.HOME and user.home_address:
            request_data["current_latitude"] = user.home_address.latitude
            request_data["current_longitude"] = user.home_address.longitude
        elif request.address_type == AddressType.WORK and user.work_address:
            request_data["current_latitude"] = user.work_address.latitude
            request_data["current_longitude"] = user.work_address.longitude

        request_ref.set(request_data)

        return request_ref.id

    async def add_custom_location(self, uid: str, location: CustomLocationCreate) -> UserInDB:
        """
        カスタム場所を追加

        Args:
            uid: ユーザーID
            location: カスタム場所データ

        Returns:
            更新後のユーザー情報

        Raises:
            ValueError: カスタム場所数が上限を超える場合
        """
        user = await self.get_user_by_uid(uid)
        if not user:
            raise ValueError("ユーザーが見つかりません")

        # カスタム場所の上限チェック（例：10箇所まで）
        if len(user.custom_locations) >= 10:
            raise ValueError("カスタム場所は最大10箇所まで登録できます")

        # 新しいカスタム場所を作成
        new_location = CustomLocation(**location.model_dump())

        # Firestoreに追加
        user_ref = self.db.collection("users").document(uid)
        user_ref.update(
            {
                "custom_locations": user.custom_locations + [new_location.model_dump(mode="json")],
                "updated_at": datetime.now(UTC),
            }
        )

        return await self.get_user_by_uid(uid)

    async def update_custom_location(
        self, uid: str, location_index: int, location: CustomLocationUpdate
    ) -> UserInDB:
        """
        カスタム場所を更新

        Args:
            uid: ユーザーID
            location_index: 更新する場所のインデックス
            location: 更新データ

        Returns:
            更新後のユーザー情報

        Raises:
            ValueError: インデックスが無効な場合
        """
        user = await self.get_user_by_uid(uid)
        if not user:
            raise ValueError("ユーザーが見つかりません")

        if location_index < 0 or location_index >= len(user.custom_locations):
            raise ValueError("無効な場所インデックスです")

        # 既存の場所を更新
        existing_location = user.custom_locations[location_index]
        update_dict = location.model_dump(exclude_unset=True, exclude_none=True)

        updated_location = existing_location.model_copy(update=update_dict)
        user.custom_locations[location_index] = updated_location

        # Firestoreを更新
        user_ref = self.db.collection("users").document(uid)
        user_ref.update(
            {
                "custom_locations": [loc.model_dump(mode="json") for loc in user.custom_locations],
                "updated_at": datetime.now(UTC),
            }
        )

        return await self.get_user_by_uid(uid)

    async def delete_custom_location(self, uid: str, location_index: int) -> UserInDB:
        """
        カスタム場所を削除

        Args:
            uid: ユーザーID
            location_index: 削除する場所のインデックス

        Returns:
            更新後のユーザー情報

        Raises:
            ValueError: インデックスが無効な場合
        """
        user = await self.get_user_by_uid(uid)
        if not user:
            raise ValueError("ユーザーが見つかりません")

        if location_index < 0 or location_index >= len(user.custom_locations):
            raise ValueError("無効な場所インデックスです")

        # 場所を削除
        user.custom_locations.pop(location_index)

        # Firestoreを更新
        user_ref = self.db.collection("users").document(uid)
        user_ref.update(
            {
                "custom_locations": [loc.model_dump(mode="json") for loc in user.custom_locations],
                "updated_at": datetime.now(UTC),
            }
        )

        return await self.get_user_by_uid(uid)

    async def get_address_change_days_remaining(
        self, uid: str, address_type: AddressType
    ) -> Optional[int]:
        """
        住所変更可能になるまでの残り日数を取得

        Args:
            uid: ユーザーID
            address_type: 住所タイプ

        Returns:
            残り日数、変更可能な場合は0、住所未登録の場合はNone
        """
        user = await self.get_user_by_uid(uid)
        if not user:
            return None

        address = user.home_address if address_type == AddressType.HOME else user.work_address

        if not address:
            return None

        days_since_change = (datetime.now(UTC) - address.last_changed_at).days
        days_remaining = settings.LOCATION_CHANGE_LOCK_DAYS - days_since_change

        return max(0, days_remaining)
