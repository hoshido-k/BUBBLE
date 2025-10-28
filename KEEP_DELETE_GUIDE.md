# 汎用APIテンプレート化ガイド

## 保持すべきファイル（✅ KEEP）

### ルートディレクトリ
```
✅ backend/                  # バックエンドAPI（汎用部分のみ）
✅ .gitignore               # Git除外設定
✅ .github/                 # GitHub Actions（後で更新）
⚠️  CLAUDE.md              # 更新必要
⚠️  README.md              # 更新必要
❌ FIREBASE_SETUP.md       # 削除（新README内に統合）
```

### Backend - API Endpoints（汎用）
```
✅ backend/app/api/v1/auth.py           # 認証API
✅ backend/app/api/v1/users.py          # ユーザー管理
✅ backend/app/api/v1/messages.py       # メッセージング
✅ backend/app/api/v1/friends.py        # フレンド機能
✅ backend/app/api/v1/notifications.py  # プッシュ通知
✅ backend/app/api/dependencies.py      # API共通依存

❌ backend/app/api/v1/locations.py     # BUBBLE固有（削除）
```

### Backend - Core & Utils（汎用）
```
✅ backend/app/core/firebase.py        # Firebase初期化
✅ backend/app/utils/jwt.py            # JWT認証
✅ backend/app/utils/security.py       # セキュリティ
✅ backend/app/utils/encryption.py     # 暗号化

⚠️  backend/app/config.py              # 更新必要（BUBBLE固有設定削除）
⚠️  backend/app/main.py                # 更新必要（locations削除）
```

### Backend - Schemas（汎用）
```
✅ backend/app/schemas/auth.py         # 認証スキーマ
✅ backend/app/schemas/user.py         # ユーザースキーマ
✅ backend/app/schemas/message.py      # メッセージスキーマ
✅ backend/app/schemas/friend.py       # フレンドスキーマ
✅ backend/app/schemas/notification.py # 通知スキーマ

❌ backend/app/schemas/location.py     # BUBBLE固有（削除）
❌ backend/app/schemas/address.py      # BUBBLE固有（削除）
```

### Backend - Services（汎用）
```
✅ backend/app/services/auth.py        # 認証サービス
✅ backend/app/services/users.py       # ユーザー管理
✅ backend/app/services/messages.py    # メッセージング
✅ backend/app/services/friends.py     # フレンド管理
✅ backend/app/services/notifications.py # 通知サービス

❌ backend/app/services/locations.py   # BUBBLE固有（削除）
```

### Backend - その他
```
✅ backend/pyproject.toml              # Python依存関係
✅ backend/uv.lock                     # uvロックファイル
✅ backend/.env.example                # 環境変数テンプレート
✅ backend/tests/                      # テスト（汎用部分のみ）

❌ backend/app/tasks/                  # BUBBLE固有（ニアミス検出など削除）
❌ backend/app/models/                 # 未使用または削除検討
```

---

## 削除すべきファイル（❌ DELETE）

### フロントエンド関連（すべて削除済み）
```
❌ mobile/                  # Flutter/React Native
❌ web/                     # Next.js
❌ shared/                  # 共有型定義
❌ lib/                     # ライブラリ
❌ docs/                    # ドキュメント
❌ firebase/                # Firebaseクライアント設定
❌ docker-compose.yml       # Docker設定
```

### BUBBLE固有機能
```
❌ backend/app/api/v1/locations.py       # 位置情報API
❌ backend/app/schemas/location.py       # 位置情報スキーマ
❌ backend/app/schemas/address.py        # 住所スキーマ
❌ backend/app/services/locations.py     # 位置情報サービス
❌ backend/app/tasks/                    # バックグラウンドタスク（ニアミス検出）
```

---

## 更新必要なファイル（⚠️ UPDATE）

### 1. backend/app/main.py
削除:
- `from app.api.v1 import locations` のインポート
- `app.include_router(locations.router, ...)` の登録
- タイトル・説明から"BUBBLE"削除

### 2. backend/app/config.py
削除:
- `APP_NAME = "BUBBLE"` → 汎用名に変更
- `HOME_RADIUS_METERS`, `WORK_RADIUS_METERS`, `SCHOOL_RADIUS_METERS`
- `NEAR_MISS_*` 関連設定
- `LOCATION_*` 関連設定

保持:
- Firebase設定
- JWT設定
- 暗号化設定

### 3. README.md
新規作成:
- 汎用APIテンプレートとしての説明
- 含まれる機能一覧（認証、メッセージング、フレンド、通知）
- セットアップ手順
- 使い方・拡張方法

### 4. CLAUDE.md
更新:
- プロジェクト概要を汎用APIとして書き換え
- BUBBLE固有の説明を削除
- 再利用方法を追加

---

## 最終的なディレクトリ構造

```
backend-api-template/
├── .github/              # GitHub Actions
├── .gitignore
├── README.md             # ⚠️ 新規作成必要
├── CLAUDE.md             # ⚠️ 更新必要
├── backend/
│   ├── .env.example
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py       # ⚠️ 更新必要
│   │   ├── config.py     # ⚠️ 更新必要
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── messages.py
│   │   │       ├── friends.py
│   │   │       └── notifications.py
│   │   ├── core/
│   │   │   └── firebase.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── message.py
│   │   │   ├── friend.py
│   │   │   └── notification.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── messages.py
│   │   │   ├── friends.py
│   │   │   └── notifications.py
│   │   └── utils/
│   │       ├── jwt.py
│   │       ├── security.py
│   │       └── encryption.py
│   └── tests/
└── KEEP_DELETE_GUIDE.md # このファイル（削除可能）
```

---

## 次のアクション

1. **手動削除** - 上記❌マークのファイルを削除
2. **ファイル更新** - main.py, config.py から BUBBLE固有設定を削除
3. **ドキュメント作成** - 新しいREADME.md, CLAUDE.md を作成
4. **テスト** - `cd backend && uv run uvicorn app.main:app --reload` で起動確認
5. **Git commit** - 変更をコミット
6. **リポジトリ名変更** - `BUBBLE` → `backend-api-template`
