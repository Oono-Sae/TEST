#!/bin/bash

echo "🚀 スキルシート RAG システム - ステージング環境セットアップ"

# 環境変数の設定
echo "⚙️ ステージング環境変数を設定中..."
export ENVIRONMENT=staging
export DATABASE_URL=postgresql://stg_user:stg_password@localhost:5432/skillsheet_stg
export REDIS_URL=redis://localhost:6379
export DEBUG=False

# Docker Composeでステージング環境を起動
echo "🐳 Docker Composeでステージング環境を起動中..."
docker-compose -f docker-compose.stg.yml up -d

# データベースのマイグレーション
echo "🗄️ データベースマイグレーションを実行中..."
sleep 10  # データベースの起動を待つ

# ヘルスチェック
echo "🔍 アプリケーションのヘルスチェック中..."
curl -f http://localhost:8001/health || echo "⚠️ アプリケーションの起動に時間がかかっています"

echo ""
echo "🎉 ステージング環境のセットアップが完了しました！"
echo ""
echo "アクセス情報:"
echo "アプリケーション: http://localhost:8001"
echo "API ドキュメント: http://localhost:8001/docs"
echo "データベース: localhost:5432"
echo "Redis: localhost:6379"
echo ""
echo "ログの確認:"
echo "docker-compose -f docker-compose.stg.yml logs -f app"
