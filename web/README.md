# BUBBLE Web App (Next.js)

BUBBLEのWebアプリケーション（管理画面・将来のWeb版）

## 技術スタック

- **Next.js 14**: React フレームワーク (App Router)
- **TypeScript**: 型安全性
- **Firebase**: 認証、Firestore
- **Tailwind CSS**: スタイリング
- **Zustand**: 状態管理

## セットアップ

### 1. 依存関係のインストール

```bash
cd web
npm install
```

### 2. 環境変数の設定

`.env.example`を`.env.local`にコピーして編集

```bash
cp .env.example .env.local
```

### 3. 開発サーバー起動

```bash
npm run dev
```

http://localhost:3000 でWebアプリが起動します

## ディレクトリ構成

```
web/
├── src/
│   ├── app/                # Next.js App Router
│   │   ├── (auth)/        # 認証画面
│   │   ├── dashboard/     # ダッシュボード
│   │   └── admin/         # 管理画面
│   ├── components/        # UIコンポーネント
│   ├── lib/              # ライブラリ（Firebase等）
│   └── types/            # TypeScript型定義
└── public/               # 静的ファイル
```

## 主要機能

### 管理画面
- ユーザー管理
- 住所変更申請の審査
- 統計・分析

### 将来のWeb版（予定）
- チャット機能
- 位置ステータス表示
- 設定管理

## よく使うコマンド

```bash
# 開発サーバー
npm run dev

# ビルド
npm run build

# 本番起動
npm run start

# Lint
npm run lint

# 型チェック
npm run type-check
```

## デプロイ

### Vercelへのデプロイ（推奨）

```bash
# Vercel CLIのインストール
npm i -g vercel

# デプロイ
vercel
```

### その他のプラットフォーム
- Firebase Hosting
- Google Cloud Run
- AWS Amplify
