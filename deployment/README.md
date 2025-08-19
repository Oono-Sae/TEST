# デプロイメントガイド

このディレクトリには、各環境へのデプロイメントに必要な設定ファイルとスクリプトが含まれています。

## 環境構成

### 1. 開発環境 (Development)
- **ポート**: 8000
- **データベース**: SQLite
- **キャッシュ**: Redis (オプション)
- **用途**: 開発・テスト

### 2. ステージング環境 (Staging)
- **ポート**: 8001
- **データベース**: PostgreSQL
- **キャッシュ**: Redis
- **リバースプロキシ**: Nginx
- **用途**: 統合テスト・ユーザー受け入れテスト

### 3. 本番環境 (Production)
- **ポート**: 8002
- **データベース**: PostgreSQL
- **キャッシュ**: Redis
- **リバースプロキシ**: Nginx (HTTPS対応)
- **用途**: 本番サービス

## デプロイメント手順

### 開発環境

```bash
# 1. セットアップスクリプトを実行
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# 2. アプリケーションを起動
cd app
python main.py
```

### ステージング環境

```bash
# 1. セットアップスクリプトを実行
chmod +x scripts/setup_stg.sh
./scripts/setup_stg.sh

# 2. Docker Composeで起動
docker-compose -f docker-compose.stg.yml up -d
```

### 本番環境

```bash
# 1. セットアップスクリプトを実行
chmod +x scripts/setup_prod.sh
./scripts/setup_prod.sh

# 2. Docker Composeで起動
docker-compose -f docker-compose.prod.yml --profile production up -d

# 3. バックアップサービスを起動 (オプション)
docker-compose -f docker-compose.prod.yml --profile backup up -d
```

## 環境変数

各環境で必要な環境変数を設定してください：

### 開発環境 (.env)
```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./skillsheet.db
REDIS_URL=redis://localhost:6379
```

### ステージング環境
```bash
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://stg_user:stg_password@localhost:5432/skillsheet_stg
REDIS_URL=redis://localhost:6379
```

### 本番環境
```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://prod_user:prod_password@localhost:5432/skillsheet_prod
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secure-secret-key
```

## セキュリティ設定

### 本番環境での必須設定

1. **SSL証明書**
   - Let's Encrypt または商用証明書を設定
   - `nginx/ssl/` ディレクトリに配置

2. **ファイアウォール**
   - 必要なポートのみ開放
   - 80, 443, 22 (SSH) のみ許可

3. **データベースセキュリティ**
   - 強力なパスワード
   - 外部からの直接アクセスを制限

4. **ログ管理**
   - ログローテーション設定
   - セキュリティログの監視

## 監視・ログ

### ログファイルの場所
- アプリケーション: `logs/app/`
- Nginx: `logs/nginx/`
- データベース: Docker ボリューム内

### ヘルスチェック
```bash
# アプリケーション
curl http://localhost:8000/health

# ステージング
curl http://localhost:8001/health

# 本番
curl http://localhost:8002/health
```

## トラブルシューティング

### よくある問題

1. **ポートが使用中**
   ```bash
   # 使用中のポートを確認
   netstat -tulpn | grep :8000
   
   # プロセスを終了
   kill -9 <PID>
   ```

2. **データベース接続エラー**
   ```bash
   # PostgreSQLの状態確認
   docker-compose logs postgres
   
   # 接続テスト
   psql -h localhost -U username -d database_name
   ```

3. **Redis接続エラー**
   ```bash
   # Redisの状態確認
   docker-compose logs redis
   
   # 接続テスト
   redis-cli ping
   ```

### ログの確認

```bash
# 全サービスのログ
docker-compose logs

# 特定サービスのログ
docker-compose logs app

# リアルタイムログ
docker-compose logs -f app
```

## バックアップ・復旧

### データベースバックアップ

```bash
# 手動バックアップ
docker-compose exec postgres pg_dump -U username database_name > backup.sql

# 自動バックアップ (本番環境)
docker-compose -f docker-compose.prod.yml --profile backup up -d
```

### 復旧手順

```bash
# データベース復旧
docker-compose exec -T postgres psql -U username database_name < backup.sql
```

## パフォーマンスチューニング

### アプリケーション設定

- ワーカー数の調整 (`--workers` パラメータ)
- メモリ制限の設定
- キャッシュ戦略の最適化

### データベース設定

- コネクションプールの調整
- インデックスの最適化
- クエリの最適化

### Nginx設定

- ワーカープロセス数の調整
- バッファサイズの最適化
- Gzip圧縮の設定
