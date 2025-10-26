#!/bin/bash

echo "🚀 Running post-create setup..."

# バックエンドのセットアップ
echo "📦 Setting up backend..."
cd /workspaces/BUBBLE/backend
if [ -f "pyproject.toml" ]; then
    uv sync
    echo "✅ Backend dependencies installed"
else
    echo "⚠️  pyproject.toml not found, skipping backend setup"
fi

# モバイルアプリのセットアップ
echo "📱 Setting up mobile app..."
cd /workspaces/BUBBLE/mobile
if [ -f "package.json" ]; then
    npm install
    echo "✅ Mobile dependencies installed"
else
    echo "⚠️  package.json not found, skipping mobile setup"
fi

# Webアプリのセットアップ
echo "🌐 Setting up web app..."
cd /workspaces/BUBBLE/web
if [ -f "package.json" ]; then
    npm install
    echo "✅ Web dependencies installed"
else
    echo "⚠️  package.json not found, skipping web setup"
fi

# 環境変数ファイルのコピー（存在しない場合）
echo "🔧 Checking environment files..."
cd /workspaces/BUBBLE

if [ ! -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from example"
fi

if [ ! -f "mobile/.env" ] && [ -f "mobile/.env.example" ]; then
    cp mobile/.env.example mobile/.env
    echo "✅ Created mobile/.env from example"
fi

if [ ! -f "web/.env.local" ] && [ -f "web/.env.example" ]; then
    cp web/.env.example web/.env.local
    echo "✅ Created web/.env.local from example"
fi

echo "✨ Setup complete! Happy coding!"
