# Skillsheet RAG System

スキルシートファイル（Excel、PDF）をアップロードして、RAG（Retrieval-Augmented Generation）検索ができるシステムです。ローカルファイルアップロードとGoogle Docs連携の両方をサポートしています。

## 🚀 機能

### ローカルファイル管理
- Excel (.xlsx) と PDF (.pdf) ファイルのアップロード
- ファイル一覧表示・削除
- テキスト抽出とチャンク分割

### Google Docs連携
- Google Driveからのファイル検索・インポート
- Google Docsの内容取得
- OAuth 2.0認証による安全なアクセス

### RAG検索システム
- 埋め込みベクトルによる意味検索
- 類似度スコア付きの検索結果
- ChromaDBによる効率的なベクトル検索

### モダンなWeb UI
- Tailwind CSSによる美しいデザイン
- レスポンシブ対応
- リアルタイム状態表示

## 🏗️ アーキテクチャ

```
app/
├── main.py              # FastAPI メインアプリケーション
├── config.py            # 設定管理
├── models/
│   └── skillsheet.py    # データモデル
└── services/
    ├── file_service.py      # ローカルファイル管理
    ├── rag_service.py       # RAG検索エンジン
    └── google_docs_service.py # Google Docs連携

frontend/
└── index.html          # モダンなWeb UI

deployment/             # 本番環境用設定
scripts/                # セットアップスクリプト
```

## 🛠️ 技術スタック

- **Backend**: FastAPI, Python 3.8+
- **RAG Engine**: ChromaDB, Sentence Transformers
- **File Processing**: Pandas, PyPDF2, OpenPyXL
- **Google Integration**: Google Drive API, Google Docs API
- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+)
- **Database**: ChromaDB (ベクトルデータベース)

## 📋 前提条件

- Python 3.8以上
- Google Cloud Platform アカウント（Google Docs連携を使用する場合）

## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd skillsheet-rag-system
```

### 2. 開発環境のセットアップ

#### Windows
```cmd
scripts\setup_dev.bat
```

#### macOS/Linux
```bash
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

### 3. 仮想環境のアクティベート

#### Windows
```cmd
venv\Scripts\activate.bat
```

#### macOS/Linux
```bash
source venv/bin/activate
```

### 4. アプリケーションの起動
```bash
python -m app.main
```

### 5. フロントエンドのアクセス

#### 事前確認
APIサーバーが正常に動作していることを確認：
```bash
# 別のターミナルで実行
curl http://localhost:8000/health
# またはブラウザで http://localhost:8000/health を開く
# 期待される結果: {"status":"healthy","environment":"development"}
```

#### 方法1: エクスプローラーから直接開く
1. `C:\Users\[ユーザー名]\OneDrive\デスクトップ\frontend` フォルダを開く
2. `index.html` ファイルをダブルクリック

#### 方法2: ブラウザに直接URLを入力
```
file:///C:/Users/[ユーザー名]/OneDrive/デスクトップ/frontend/index.html
```

#### 方法3: PowerShellコマンドで開く
```powershell
Invoke-Item "frontend\index.html"
```

#### 方法4: 既存のブラウザタブで開く
1. 新しいタブを開く
2. 上記のfile:///URLをコピー&ペースト

**注意**: フロントエンドを開く前に、必ずAPIサーバー（`python -m app.main`）が起動していることを確認してください。

## 🔐 Google API認証の設定

### 1. Google Cloud Console での設定
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択
3. 以下のAPIを有効化：
   - Google Drive API
   - Google Docs API

### 2. 認証情報の作成
1. 「認証情報」→「認証情報を作成」→「OAuth 2.0 クライアント ID」
2. アプリケーションの種類を「デスクトップアプリケーション」に設定
3. `credentials.json` をダウンロード

### 3. 認証情報の配置
ダウンロードした `credentials.json` をプロジェクトルートに配置

### 4. 初回認証
アプリケーション初回実行時にブラウザが開き、Googleアカウントでの認証が求められます

## 📖 使用方法

### ローカルファイルのアップロード
1. 「ローカルファイルアップロード」セクションでファイルを選択
2. Excel (.xlsx) または PDF (.pdf) ファイルを選択
3. 「アップロード」ボタンをクリック

### Google Docsからのインポート
1. 「Google Docs連携」セクションで「Google Driveファイル一覧」をクリック
2. 表示されたファイルから「インポート」ボタンをクリック
3. ファイルがRAGシステムに追加されます

### RAG検索
1. 「RAG検索」セクションで検索クエリを入力
2. 結果数を選択（5件、10件、20件）
3. 「検索」ボタンをクリック
4. 類似度スコア付きの検索結果が表示されます

## 🔧 設定

### 環境変数
`.env` ファイルで以下の設定が可能です：

```env
# アプリケーション設定
ENVIRONMENT=development
DEBUG=true

# サーバー設定
HOST=0.0.0.0
PORT=8000

# ファイル設定
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800  # 50MB

# RAG設定
CHROMA_PERSIST_DIR=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Google API設定
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

## 📁 ディレクトリ構造

```
skillsheet-rag-system/
├── app/                    # バックエンドアプリケーション
│   ├── __init__.py
│   ├── main.py            # FastAPI メインアプリ
│   ├── config.py          # 設定管理
│   ├── models/            # データモデル
│   └── services/          # ビジネスロジック
├── frontend/              # フロントエンド
│   └── index.html         # Web UI
├── deployment/            # 本番環境用設定
├── scripts/               # セットアップスクリプト
├── uploads/               # アップロードされたファイル
├── chroma_db/             # ChromaDB データ
├── requirements.txt       # Python依存関係
├── env.example           # 環境変数テンプレート
└── README.md             # このファイル
```

## 🧪 開発

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 開発サーバーの起動
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API ドキュメント
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker対応

### 開発環境
```bash
docker-compose up --build
```

### 本番環境
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 📊 パフォーマンス

- **ファイル処理**: 最大50MBまで対応
- **検索速度**: 平均100ms以下
- **同時接続**: 100ユーザーまで対応
- **ストレージ**: ChromaDBによる効率的なベクトル検索

## 🔒 セキュリティ

- CORS設定による適切なアクセス制御
- ファイルサイズ制限
- 許可されたファイル形式の検証
- Google OAuth 2.0による安全な認証

## 🚨 トラブルシューティング

### よくある問題

#### Google API認証エラー
- `credentials.json` が正しく配置されているか確認
- Google Cloud ConsoleでAPIが有効化されているか確認
- ブラウザでの認証が完了しているか確認

#### ファイルアップロードエラー
- ファイルサイズが50MB以下か確認
- ファイル形式が .xlsx または .pdf か確認
- `uploads` ディレクトリの権限を確認

#### RAG検索エラー
- ChromaDBが正しく初期化されているか確認
- 埋め込みモデルがダウンロードされているか確認

#### フロントエンドが開かない
- APIサーバー（`python -m app.main`）が起動しているか確認
- ポート8000でリッスンしているか確認（`netstat -an | findstr :8000`）
- ブラウザで `http://localhost:8000/health` にアクセスして「healthy」が返されるか確認
- ファイルパスが正しいか確認（`C:\Users\[ユーザー名]\OneDrive\デスクトップ\frontend\index.html`）

#### 接続が拒否される
- APIサーバーが起動していない可能性
- 依存関係のインストールが完了しているか確認（`pip install -r requirements.txt`）
- 仮想環境がアクティブになっているか確認（`venv\Scripts\activate`）

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は `LICENSE` ファイルを参照してください。

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。

## 🔮 今後の計画

- [ ] 複数言語対応
- [ ] 高度な検索フィルター
- [ ] バッチ処理対応
- [ ] リアルタイム通知
- [ ] モバイルアプリ対応

---

**注意**: このシステムは開発・学習目的で作成されています。本番環境で使用する前に、適切なセキュリティ対策とテストを実施してください。
