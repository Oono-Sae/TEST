from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from typing import List, Optional
import logging

from .services.file_service import FileService
from .services.rag_service import RAGService
from .services.google_docs_service import GoogleDocsService
from .services.gpt_service import GPTService
from .models.skillsheet import SkillsheetResponse, SearchResponse
from .config import settings

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Skillsheet RAG System",
    description="スキルシートファイルをアップロードしてRAG検索ができるシステム（ローカルファイル + Google Docs対応）",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# サービス初期化
file_service = FileService()
rag_service = RAGService()
google_docs_service = GoogleDocsService()
gpt_service = GPTService()

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Skillsheet RAG System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/google-auth-status")
async def google_auth_status():
    """Google認証状態を確認"""
    return {
        "authenticated": google_docs_service.is_authenticated(),
        "message": "Google認証状態を確認しました"
    }

@app.post("/upload", response_model=SkillsheetResponse)
async def upload_skillsheet(file: UploadFile = File(...)):
    """スキルシートファイルをアップロード"""
    try:
        # ファイル形式チェック
        if not file.filename.lower().endswith(('.xlsx', '.pdf')):
            raise HTTPException(
                status_code=400, 
                detail="サポートされているファイル形式は .xlsx と .pdf のみです"
            )
        
        # ファイル保存
        saved_path = await file_service.save_file(file)
        
        # RAGシステムに追加
        await rag_service.add_document(saved_path, file.filename)
        
        return SkillsheetResponse(
            filename=file.filename,
            file_path=str(saved_path),
            message="ファイルが正常にアップロードされ、RAGシステムに追加されました"
        )
        
    except Exception as e:
        logger.error(f"ファイルアップロードエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/google-docs/import")
async def import_from_google_docs(file_id: str = Form(...), filename: str = Form(...)):
    """Google Docsからファイルをインポート"""
    try:
        if not google_docs_service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="Google認証が必要です。credentials.jsonを設定してください。"
            )
        
        # Google Driveからファイルをダウンロード
        temp_file = await google_docs_service.download_file(file_id, filename)
        if not temp_file:
            raise HTTPException(
                status_code=500,
                detail="Google Driveからのファイルダウンロードに失敗しました"
            )
        
        # RAGシステムに追加
        await rag_service.add_document(temp_file, filename)
        
        return SkillsheetResponse(
            filename=filename,
            file_path=str(temp_file),
            message="Google Docsからファイルが正常にインポートされ、RAGシステムに追加されました"
        )
        
    except Exception as e:
        logger.error(f"Google Docsインポートエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-docs/files")
async def list_google_docs_files(folder_id: Optional[str] = Query(None)):
    """Google Driveのスキルシートファイル一覧を取得"""
    try:
        if not google_docs_service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="Google認証が必要です。credentials.jsonを設定してください。"
            )
        
        files = await google_docs_service.list_skillsheets(folder_id)
        return {"files": files, "message": "Google Driveファイル一覧を取得しました"}
        
    except Exception as e:
        logger.error(f"Google Driveファイル一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google-docs/search")
async def search_google_docs_files(query: str = Query(...)):
    """Google Driveでファイルを検索"""
    try:
        if not google_docs_service.is_authenticated():
            raise HTTPException(
                status_code=401,
                detail="Google認証が必要です。credentials.jsonを設定してください。"
            )
        
        files = await google_docs_service.search_files(query)
        return {"files": files, "query": query, "message": "Google Drive検索が完了しました"}
        
    except Exception as e:
        logger.error(f"Google Drive検索エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_model=List[SkillsheetResponse])
async def list_files():
    """アップロードされたファイル一覧を取得"""
    try:
        files = await file_service.list_files()
        return files
    except Exception as e:
        logger.error(f"ファイル一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_skillsheets(query: str = Form(...), n_results: int = Query(10)):
    """スキルシートを検索"""
    try:
        results = await rag_service.search(query, n_results)
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            message="検索が完了しました"
        )
    except Exception as e:
        logger.error(f"検索エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/collection-info")
async def get_rag_collection_info():
    """RAGコレクション情報を取得"""
    try:
        info = await rag_service.get_collection_info()
        return {"collection_info": info, "message": "コレクション情報を取得しました"}
    except Exception as e:
        logger.error(f"コレクション情報取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/clear")
async def clear_rag_collection():
    """RAGコレクションをクリア"""
    try:
        success = await rag_service.clear_collection()
        if success:
            return {"message": "RAGコレクションがクリアされました"}
        else:
            raise HTTPException(status_code=500, detail="コレクションのクリアに失敗しました")
    except Exception as e:
        logger.error(f"コレクションクリアエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """ファイルを削除"""
    try:
        await file_service.delete_file(filename)
        await rag_service.remove_document(filename)
        return {"message": f"ファイル {filename} が削除されました"}
    except Exception as e:
        logger.error(f"ファイル削除エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gpt/generate-answer")
async def generate_gpt_answer(query: str = Form(...), n_results: int = Query(5)):
    """GPTを使用して質問に対する回答を生成"""
    try:
        if not gpt_service.is_available():
            raise HTTPException(
                status_code=400,
                detail="GPTサービスが利用できません。OpenAI APIキーを設定してください。"
            )
        
        # まずRAG検索で関連情報を取得
        search_results = await rag_service.search(query, n_results)
        
        if not search_results:
            return {
                "query": query,
                "answer": "申し訳ございませんが、質問に関連する情報が見つかりませんでした。",
                "context": [],
                "message": "関連情報なしで回答を生成しました"
            }
        
        # GPTで回答を生成
        answer = await gpt_service.generate_answer(query, search_results)
        
        if not answer:
            raise HTTPException(
                status_code=500,
                detail="GPT回答の生成に失敗しました"
            )
        
        return {
            "query": query,
            "answer": answer,
            "context": search_results,
            "message": "GPT回答を生成しました"
        }
        
    except Exception as e:
        logger.error(f"GPT回答生成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gpt/status")
async def get_gpt_status():
    """GPTサービスの状態を確認"""
    return {
        "available": gpt_service.is_available(),
        "model": gpt_service.model if gpt_service.is_available() else None,
        "message": "GPTサービス状態を確認しました"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
