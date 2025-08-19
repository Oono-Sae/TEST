@echo off
echo 🚀 Skillsheet RAG System - 開発環境セットアップを開始します...

REM 必要なディレクトリを作成
echo 📁 必要なディレクトリを作成中...
if not exist "uploads" mkdir uploads
if not exist "chroma_db" mkdir chroma_db
if not exist "logs" mkdir logs

REM Python仮想環境を作成
echo 🐍 Python仮想環境を作成中...
python -m venv venv

REM 仮想環境をアクティベート
echo 🔧 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

REM 依存関係をインストール
echo 📦 依存関係をインストール中...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 環境設定ファイルを作成
echo ⚙️ 環境設定ファイルを作成中...
if not exist ".env" (
    copy env.example .env
    echo ✅ .env ファイルが作成されました。必要に応じて設定を編集してください。
) else (
    echo ℹ️ .env ファイルは既に存在します。
)

echo.
echo 🔐 Google API認証の設定:
echo 1. Google Cloud Console (https://console.cloud.google.com/) にアクセス
echo 2. 新しいプロジェクトを作成または既存のプロジェクトを選択
echo 3. Google Drive API と Google Docs API を有効化
echo 4. 認証情報を作成 -^> OAuth 2.0 クライアント ID
echo 5. ダウンロードした credentials.json をプロジェクトルートに配置
echo 6. 初回実行時にブラウザが開き、Googleアカウントで認証
echo.

echo.
echo ✅ セットアップが完了しました！
echo.
echo 次のコマンドでアプリケーションを起動できます：
echo venv\Scripts\activate.bat
echo python -m app.main
echo.
echo または、フロントエンドを開くには：
echo start frontend\index.html
echo.
echo 📚 詳細な使用方法は README.md を参照してください。

pause
