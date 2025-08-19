#!/bin/bash

echo "🚀 Skillsheet RAG System - 開発環境を起動します..."

# 仮想環境をアクティベート
if [ -d "venv" ]; then
    echo "🔧 仮想環境をアクティベート中..."
    source venv/bin/activate
else
    echo "❌ 仮想環境が見つかりません。先に setup_dev.sh を実行してください。"
    exit 1
fi

# 必要なディレクトリを作成
echo "📁 必要なディレクトリを確認中..."
mkdir -p uploads chroma_db logs

# 環境設定ファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️ .env ファイルが見つかりません。env.example からコピーします..."
    cp env.example .env
    echo "✅ .env ファイルが作成されました。必要に応じて設定を編集してください。"
fi

# Google認証情報の確認
if [ ! -f "credentials.json" ]; then
    echo "⚠️ credentials.json が見つかりません。Google Docs連携は利用できません。"
    echo "Google Cloud Console から credentials.json をダウンロードして配置してください。"
fi

# アプリケーションを起動
echo "🚀 アプリケーションを起動中..."
echo "📱 フロントエンド: http://localhost:8000"
echo "📚 API ドキュメント: http://localhost:8000/docs"
echo "🔍 ReDoc: http://localhost:8000/redoc"
echo ""
echo "停止するには Ctrl+C を押してください。"
echo ""

python -m app.main
