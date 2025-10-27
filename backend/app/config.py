from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # アプリケーション設定
    APP_NAME: str = "BUBBLE"
    DEBUG: bool = False

    # Firebase設定
    FIREBASE_PROJECT_ID: str
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # JWT設定
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 位置情報設定
    HOME_RADIUS_METERS: int = 200  # 自宅判定半径
    WORK_RADIUS_METERS: int = 500  # 職場判定半径（社会人）
    SCHOOL_RADIUS_METERS: int = 500  # 学校判定半径（学生）
    LOCATION_CHANGE_LOCK_DAYS: int = 90  # 住所変更制限日数

    # ニアミス検出設定
    NEAR_MISS_RADIUS_METERS: int = 50  # ニアミス判定半径
    NEAR_MISS_TIME_DIFF_MINUTES: int = 30  # ニアミス時間差
    LOCATION_HISTORY_RETENTION_DAYS: int = 7  # 位置履歴保持期間

    # 暗号化設定
    ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
