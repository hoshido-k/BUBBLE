# Dev Container 設定

BUBBLEプロジェクトのVS Code Dev Container設定です。

## 🎯 含まれる環境

### 言語・ランタイム
- **Python 3.11**: バックエンド開発
- **uv**: 高速Pythonパッケージマネージャー
- **Node.js 20**: フロントエンド開発
- **npm, pnpm, yarn**: パッケージマネージャー

### ツール
- **Expo CLI**: React Native開発
- **EAS CLI**: Expoビルドサービス
- **Firebase CLI**: Firebaseデプロイ
- **Google Cloud SDK**: GCPデプロイ（オプション）
- **Git, GitHub CLI**: バージョン管理

### VS Code 拡張機能
- Python (Pylance, Ruff)
- ESLint, Prettier
- React Native Tools
- GitLens
- Docker
- その他開発支援ツール

## 🚀 使い方

### 1. 前提条件
- VS Code
- Docker Desktop
- Dev Containers拡張機能

### 2. コンテナで開く

```
1. VS Codeでプロジェクトを開く
2. コマンドパレット (Cmd+Shift+P) を開く
3. "Dev Containers: Reopen in Container" を選択
4. 初回は構築に5-10分かかります
```

### 3. 自動セットアップ

コンテナ起動後、以下が自動実行されます：
- バックエンドの依存関係インストール（uv sync）
- モバイルアプリの依存関係インストール（npm install）
- Webアプリの依存関係インストール（npm install）
- 環境変数ファイルのコピー（.env.example → .env）

### 4. 開発サーバーの起動

```bash
# バックエンド
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0

# モバイル
cd mobile
npm start

# Web
cd web
npm run dev
```

## 📁 構成

```
.devcontainer/
├── devcontainer.json        # メイン設定
├── Dockerfile              # 開発環境イメージ
├── docker-compose.yml      # コンテナ構成
├── post-create.sh          # セットアップスクリプト
└── README.md               # このファイル
```

## 🔧 カスタマイズ

### 拡張機能の追加

`devcontainer.json`の`extensions`配列に追加：

```json
"extensions": [
  "your-extension-id"
]
```

### ポートフォワードの追加

`devcontainer.json`の`forwardPorts`配列に追加：

```json
"forwardPorts": [8000, 3000, 19000, 5000]
```

## ⚠️ トラブルシューティング

### コンテナが起動しない
```bash
# キャッシュをクリアして再構築
docker-compose -f .devcontainer/docker-compose.yml down -v
docker system prune -a
# VS Codeで "Rebuild Container" を実行
```

### 依存関係がインストールされない
```bash
# コンテナ内で手動実行
cd backend && uv sync
cd mobile && npm install
cd web && npm install
```

### ポートが競合する
`devcontainer.json`の`forwardPorts`を変更して競合を回避

## 💡 ヒント

- コンテナ内のターミナルは自動的にzshになります
- Git認証情報はホストから自動的に継承されます
- ファイル変更は自動的に同期されます（cached volume使用）
- 拡張機能の設定は自動適用されます
