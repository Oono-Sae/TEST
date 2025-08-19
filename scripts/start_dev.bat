@echo off
echo 🚀 Skillsheet RAG System - 開発環境を起動します...

REM 仮想環境をアクティベート
if exist "venv" (
    echo 🔧 仮想環境をアクティベート中...
    call venv\Scripts\activate.bat
) else (
    echo ❌ 仮想環境が見つかりません。先に setup_dev.bat を実行してください。
    pause
    exit /b 1
)

REM 必要なディレクトリを作成
echo 📁 必要なディレクトリを確認中...
if not exist "uploads" mkdir uploads
if not exist "chroma_db" mkdir chroma_db
if not exist "logs" mkdir logs

REM 環境設定ファイルの確認
if not exist ".env" (
    echo ⚠️ .env ファイルが見つかりません。env.example からコピーします...
    copy env.example .env
    echo ✅ .env ファイルが作成されました。必要に応じて設定を編集してください。
)

REM Google認証情報の確認
if not exist "credentials.json" (
    echo ⚠️ credentials.json が見つかりません。Google Docs連携は利用できません。
    echo Google Cloud Console から credentials.json をダウンロードして配置してください。
)

REM アプリケーションを起動
echo 🚀 アプリケーションを起動中...
echo 📱 フロントエンド: http://localhost:8000
echo 📚 API ドキュメント: http://localhost:8000/docs
echo 🔍 ReDoc: http://localhost:8000/redoc
echo.
echo 停止するには Ctrl+C を押してください。
echo.

python -m app.main

pause
