from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, friends, locations, users
from app.core.firebase import initialize_firebase

# TODO: 他のルーターは実装後にインポート
# from app.api.v1 import messages, notifications, near_miss

app = FastAPI(
    title="BUBBLE API",
    description="Be Unseen, Be Loved, Everywhere - API Server",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase初期化（一時的にコメントアウト - Firebaseセットアップ後に有効化）
# initialize_firebase()

# ルーター登録
app.include_router(auth.router, prefix="/api/v1/auth", tags=["認証"])
app.include_router(users.router, prefix="/api/v1/users", tags=["ユーザー"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["位置情報"])
app.include_router(friends.router, prefix="/api/v1/friends", tags=["フレンド"])
# TODO: 他のルーターは実装後に登録
# app.include_router(messages.router, prefix="/api/v1/messages", tags=["メッセージ"])
# app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["通知"])
# app.include_router(near_miss.router, prefix="/api/v1/near-miss", tags=["ニアミス"])

@app.get("/")
async def root():
    return {"message": "BUBBLE API Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
