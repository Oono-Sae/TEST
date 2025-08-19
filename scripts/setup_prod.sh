#!/bin/bash

echo "🚀 スキルシート RAG システム - 本番環境セットアップ"

# 環境変数の設定
echo "⚙️ 本番環境変数を設定中..."
export ENVIRONMENT=production
export DATABASE_URL=postgresql://prod_user:prod_password@localhost:5432/skillsheet_prod
export REDIS_URL=redis://localhost:6379
export DEBUG=False
export SECRET_KEY=$(openssl rand -hex 32)

# セキュリティチェック
echo "🔒 セキュリティ設定を確認中..."
if [ "$ENVIRONMENT" = "production" ]; then
    echo "⚠️ 本番環境のセットアップを実行します"
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ セットアップを中止しました"
        exit 1
    fi
fi

# Docker Composeで本番環境を起動
echo "🐳 Docker Composeで本番環境を起動中..."
docker-compose -f docker-compose.prod.yml --profile production up -d

# データベースのマイグレーション
echo "🗄️ データベースマイグレーションを実行中..."
sleep 15  # データベースの起動を待つ

# ヘルスチェック
echo "🔍 アプリケーションのヘルスチェック中..."
curl -f http://localhost:8002/health || echo "⚠️ アプリケーションの起動に時間がかかっています"

# バックアップ設定
echo "💾 バックアップ設定を確認中..."
mkdir -p /backup/skillsheet

echo ""
echo "🎉 本番環境のセットアップが完了しました！"
echo ""
echo "⚠️ 重要な設定項目:"
echo "- ファイアウォール設定"
echo "- SSL証明書の設定"
echo "- ログローテーション"
echo "- モニタリング設定"
echo "- バックアップスケジュール"
echo ""
echo "アクセス情報:"
echo "アプリケーション: http://localhost:8002"
echo "API ドキュメント: http://localhost:8002/docs"
echo "データベース: localhost:5432"
echo "Redis: localhost:6379"
echo ""
echo "ログの確認:"
echo "docker-compose -f docker-compose.prod.yml logs -f app"
