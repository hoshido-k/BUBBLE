# BUBBLE Mobile App (React Native + Expo)

BUBBLEのモバイルアプリケーション（iOS/Android対応）

## 技術スタック

- **React Native**: クロスプラットフォームモバイルアプリ開発
- **Expo**: React Nativeの開発環境
- **Expo Router**: ファイルベースルーティング
- **Firebase**: 認証、Firestore、Storage、FCM
- **Zustand**: 状態管理
- **TypeScript**: 型安全性

## セットアップ

### 1. Node.jsのインストール

Node.js 18以上が必要です

### 2. 依存関係のインストール

```bash
cd mobile
npm install
```

### 3. 環境変数の設定

`.env.example`を`.env`にコピーして編集

```bash
cp .env.example .env
```

### 4. 開発サーバー起動

```bash
npm start
```

開発用アプリでQRコードをスキャンして起動

### 5. プラットフォーム別起動

```bash
# iOS
npm run ios

# Android
npm run android

# Web
npm run web
```

## ディレクトリ構成

```
mobile/
├── app/                     # Expo Router (画面)
│   ├── (auth)/             # 認証画面
│   ├── (tabs)/             # メインタブ画面
│   ├── chat/               # チャット画面
│   ├── profile/            # プロフィール
│   └── location/           # 位置情報設定
├── src/
│   ├── components/         # UIコンポーネント
│   ├── hooks/              # カスタムフック
│   ├── services/           # API通信・Firebase
│   ├── store/              # 状態管理
│   ├── utils/              # ユーティリティ
│   ├── types/              # TypeScript型定義
│   └── constants/          # 定数
└── assets/                 # 画像・アイコン
```

## 主要機能

### 位置情報追跡
- フォアグラウンド位置取得: `expo-location`
- バックグラウンド追跡: `expo-task-manager`
- ステータス判定: バックエンドAPIで処理

### 認証・セキュリティ
- Firebase Authentication
- 生体認証: `expo-local-authentication`
- 不正アクセス検知

### リアルタイムメッセージング
- Firestore リアルタイムリスナー
- プッシュ通知: Firebase Cloud Messaging

## よく使うコマンド

```bash
# 依存関係の追加
npm install <package-name>

# 型チェック
npm run type-check

# Linter
npm run lint

# フォーマット
npm run format

# ビルド (EAS Build使用)
eas build --platform ios
eas build --platform android
```

## デプロイ

### EAS Buildを使用したビルド

```bash
# EAS CLIのインストール
npm install -g eas-cli

# ログイン
eas login

# ビルド設定
eas build:configure

# iOS/Androidビルド
eas build --platform all

# アプリストア提出
eas submit
```
