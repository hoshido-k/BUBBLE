# Firebase セットアップガイド

## 1. Firebase プロジェクトの作成

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. 「プロジェクトを追加」をクリック
3. プロジェクト名: `BUBBLE` (または任意の名前)
4. Google Analytics: オフ (またはオン、お好みで)
5. プロジェクトを作成

## 2. サービスアカウントキーの取得

1. Firebase Console で作成したプロジェクトを開く
2. 左メニューの歯車アイコン → 「プロジェクトの設定」
3. 「サービス アカウント」タブをクリック
4. 「新しい秘密鍵の生成」をクリック
5. ダウンロードされたJSONファイルを `backend/firebase-credentials.json` として保存

## 3. Firebase Authentication の有効化

1. Firebase Console 左メニューの「Authentication」
2. 「始める」をクリック
3. 「Sign-in method」タブ
4. 「メール/パスワード」を有効化
5. 保存

## 4. Cloud Firestore の有効化

1. Firebase Console 左メニューの「Firestore Database」
2. 「データベースを作成」をクリック
3. **テストモードで開始** (開発用)
4. ロケーション: `asia-northeast1` (東京) または最寄りのリージョン
5. 有効にする

## 5. Cloud Messaging (FCM) の有効化

1. Firebase Console 左メニューの「Cloud Messaging」
2. 自動的に有効化されます
3. サーバーキーとSender IDをメモ（モバイルアプリで使用）

## 6. .env ファイルの設定

`backend/.env` を編集：

```bash
# Firebase設定
FIREBASE_PROJECT_ID=your-actual-project-id  # Firebase Consoleで確認
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# JWT設定（変更推奨）
SECRET_KEY=ランダムな長い文字列に変更してください
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 暗号化キー（変更推奨）
ENCRYPTION_KEY=32バイトのランダムな文字列

# アプリケーション設定
DEBUG=True
```

### ランダムキーの生成方法

Pythonで生成：
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 7. Firestore セキュリティルールの設定（開発後）

本番環境では適切なセキュリティルールを設定してください：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 開発中はテストモード（全許可）
    // 本番環境では適切な制限を設定
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 8. 設定の確認

バックエンドサーバーを起動してエラーがないか確認：

```bash
cd backend
uv run uvicorn app.main:app --reload
```

http://localhost:8000/docs でAPI ドキュメントが表示されればOK！

## トラブルシューティング

### エラー: "Could not load the default credentials"
- `firebase-credentials.json` のパスが正しいか確認
- ファイルの中身が有効なJSONか確認

### エラー: "Permission denied"
- Firestoreが有効化されているか確認
- セキュリティルールがテストモードになっているか確認

### エラー: "Invalid project ID"
- `.env` の `FIREBASE_PROJECT_ID` がFirebase Consoleの値と一致しているか確認
