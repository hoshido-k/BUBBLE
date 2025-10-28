"""
ユーザー管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencies import get_current_user
from app.schemas.address import (
    AddressType,
    AddressUpdateRequest,
    CustomLocationCreate,
    CustomLocationUpdate,
    SpecialAddressChangeRequest,
)
from app.schemas.user import UserDetailResponse, UserInDB, UserResponse, UserUpdate
from app.services.users import UserService

router = APIRouter()


@router.get("/{uid}", response_model=UserResponse)
async def get_user(
    uid: str = Path(..., description="ユーザーID"),
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    ユーザー情報を取得（公開情報のみ）

    他のユーザーのプロフィールを取得する際に使用します。

    Args:
        uid: 取得するユーザーのID
        current_user: 現在のユーザー（認証必須）
        user_service: ユーザーサービス

    Returns:
        ユーザーの公開情報
    """
    user = await user_service.get_user_by_uid(uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません"
        )

    return UserResponse(
        uid=user.uid,
        email=user.email,
        display_name=user.display_name,
        profile_image_url=user.profile_image_url,
        created_at=user.created_at,
    )


@router.patch("/me", response_model=UserDetailResponse)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    自分のプロフィールを更新

    表示名やプロフィール画像URLを更新できます。

    Args:
        update_data: 更新データ
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Returns:
        更新後のユーザー詳細情報
    """
    try:
        updated_user = await user_service.update_profile(current_user.uid, update_data)
        return UserDetailResponse(**updated_user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/me/address/{address_type}", response_model=UserDetailResponse)
async def update_address(
    address_type: AddressType = Path(..., description="住所タイプ（home/work）"),
    address_data: AddressUpdateRequest = ...,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    住所を更新（90日制限あり）

    自宅または職場の住所を更新します。
    90日間の変更制限があり、制限期間内の場合はエラーになります。

    Args:
        address_type: 住所タイプ（home/work）
        address_data: 新しい住所データ
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Returns:
        更新後のユーザー詳細情報

    Raises:
        HTTPException: 変更制限期間内の場合
    """
    try:
        updated_user = await user_service.update_address(
            current_user.uid, address_type, address_data
        )
        return UserDetailResponse(**updated_user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me/address/{address_type}/change-status")
async def get_address_change_status(
    address_type: AddressType = Path(..., description="住所タイプ（home/work）"),
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    住所変更可能状態を取得

    住所が変更可能かどうか、および変更可能になるまでの残り日数を返します。

    Args:
        address_type: 住所タイプ
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Returns:
        変更可能状態と残り日数
    """
    can_change = await user_service.can_change_address(current_user.uid, address_type)
    days_remaining = await user_service.get_address_change_days_remaining(
        current_user.uid, address_type
    )

    return {
        "can_change": can_change,
        "days_remaining": days_remaining,
        "lock_days": 90,  # 設定から取得
        "address_type": address_type.value,
    }


@router.post("/me/address/special-change-request")
async def create_special_address_change_request(
    request: SpecialAddressChangeRequest,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    特別な住所変更申請を作成

    引っ越しや転職など、やむを得ない理由で90日制限内に住所を変更する必要がある場合に申請します。
    運営の承認が必要です。

    Args:
        request: 変更申請データ
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Returns:
        申請ID
    """
    try:
        request_id = await user_service.create_special_address_change_request(
            current_user.uid, request
        )
        return {
            "message": "住所変更申請を受け付けました",
            "request_id": request_id,
            "status": "pending",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/me/custom-locations", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def add_custom_location(
    location: CustomLocationCreate,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    カスタム場所を追加

    よく行くカフェ、ジムなどのカスタム場所を追加します。
    最大10箇所まで登録できます。

    Args:
        location: カスタム場所データ
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Returns:
        更新後のユーザー詳細情報
    """
    try:
        updated_user = await user_service.add_custom_location(current_user.uid, location)
        return UserDetailResponse(**updated_user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/me/custom-locations/{location_index}", response_model=UserDetailResponse)
async def update_custom_location(
    location_index: int = Path(..., ge=0, description="場所のインデックス"),
    location: CustomLocationUpdate = ...,
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    カスタム場所を更新

    名前、半径、色などを更新できます。

    Args:
        location_index: 更新する場所のインデックス
        location: 更新データ
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Returns:
        更新後のユーザー詳細情報
    """
    try:
        updated_user = await user_service.update_custom_location(
            current_user.uid, location_index, location
        )
        return UserDetailResponse(**updated_user.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/me/custom-locations/{location_index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_location(
    location_index: int = Path(..., ge=0, description="場所のインデックス"),
    current_user: UserInDB = Depends(get_current_user),
    user_service: UserService = Depends(lambda: UserService()),
):
    """
    カスタム場所を削除

    Args:
        location_index: 削除する場所のインデックス
        current_user: 現在のユーザー
        user_service: ユーザーサービス

    Raises:
        HTTPException: インデックスが無効な場合
    """
    try:
        await user_service.delete_custom_location(current_user.uid, location_index)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
