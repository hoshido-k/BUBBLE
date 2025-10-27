"""
位置情報APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.dependencies import get_current_user
from app.schemas.location import (
    CurrentLocationResponse,
    LocationHistoryResponse,
    LocationResponse,
    LocationUpdateRequest,
)
from app.schemas.user import UserInDB
from app.services.locations import LocationService

router = APIRouter()


@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_200_OK)
async def update_location(
    location_data: LocationUpdateRequest,
    current_user: UserInDB = Depends(get_current_user),
    location_service: LocationService = Depends(lambda: LocationService()),
):
    """
    現在位置を更新

    位置情報（緯度、経度、速度など）を送信して、現在のステータスを更新します。
    位置情報は暗号化されて保存されます。

    Args:
        location_data: 位置情報データ
        current_user: 現在のユーザー
        location_service: 位置情報サービス

    Returns:
        更新後の位置情報ステータス
    """
    try:
        result = await location_service.update_location(current_user.uid, location_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"位置情報の更新に失敗しました: {str(e)}",
        )


@router.get("/current", response_model=CurrentLocationResponse)
async def get_current_location(
    current_user: UserInDB = Depends(get_current_user),
    location_service: LocationService = Depends(lambda: LocationService()),
):
    """
    自分の現在位置ステータスを取得

    現在の位置ステータス（自宅、職場、学校、移動中など）を取得します。

    Args:
        current_user: 現在のユーザー
        location_service: 位置情報サービス

    Returns:
        現在の位置情報
    """
    location = await location_service.get_current_location(current_user.uid)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="位置情報が見つかりません"
        )
    return location


@router.get("/history", response_model=LocationHistoryResponse)
async def get_location_history(
    days: int = Query(7, ge=1, le=7, description="取得する日数（1-7日）"),
    current_user: UserInDB = Depends(get_current_user),
    location_service: LocationService = Depends(lambda: LocationService()),
):
    """
    位置履歴を取得

    過去の位置情報ステータス履歴を取得します。
    最大7日分まで取得できます。

    Args:
        days: 取得する日数（1-7日、デフォルト7日）
        current_user: 現在のユーザー
        location_service: 位置情報サービス

    Returns:
        位置履歴
    """
    try:
        history = await location_service.get_location_history(current_user.uid, days)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"位置履歴の取得に失敗しました: {str(e)}",
        )


@router.get("/friend/{friend_id}", response_model=CurrentLocationResponse)
async def get_friend_location(
    friend_id: str = Path(..., description="フレンドのユーザーID"),
    current_user: UserInDB = Depends(get_current_user),
    location_service: LocationService = Depends(lambda: LocationService()),
):
    """
    フレンドの現在位置を取得

    フレンド登録しているユーザーの現在位置ステータスを取得します。
    フレンド関係がない場合はエラーになります。

    Args:
        friend_id: フレンドのユーザーID
        current_user: 現在のユーザー
        location_service: 位置情報サービス

    Returns:
        フレンドの現在位置情報

    Raises:
        HTTPException: フレンド関係がない、または位置情報が見つからない場合
    """
    try:
        location = await location_service.get_friend_location(current_user.uid, friend_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="フレンドの位置情報が見つかりません",
            )
        return location
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"位置情報の取得に失敗しました: {str(e)}",
        )
