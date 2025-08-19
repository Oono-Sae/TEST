import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from ..config import settings
from ..services.file_service import FileService
from ..models.skillsheet import SearchResult

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # コレクション名
        self.collection_name = "skillsheets"
        
        # コレクションの取得または作成
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            logger.info(f"既存のコレクション '{self.collection_name}' を取得しました")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "スキルシートのRAG検索用コレクション"}
            )
            logger.info(f"新しいコレクション '{self.collection_name}' を作成しました")
        
        # ファイルサービス
        self.file_service = FileService()
        
        # 埋め込みモデルの初期化
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"埋め込みモデル '{settings.EMBEDDING_MODEL}' を初期化しました")
    
    async def add_document(self, file_path: Path, filename: str) -> bool:
        """ドキュメントをRAGシステムに追加"""
        try:
            # ファイルからテキストを抽出
            text_content = await self.file_service.extract_text(file_path)
            
            if not text_content.strip():
                logger.warning(f"ファイル '{filename}' からテキストが抽出できませんでした")
                return False
            
            # テキストをチャンクに分割
            chunks = self._split_text_into_chunks(text_content)
            
            # 埋め込みを一括計算
            embeddings = self.embedding_model.encode(chunks, convert_to_numpy=False)

            # 追加用データを構築
            ids = []
            metadatas = []
            for i, chunk in enumerate(chunks):
                ids.append(f"{filename}_chunk_{i}")
                metadatas.append({
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_path": str(file_path),
                    "chunk_size": len(chunk)
                })

            # コレクションに一括追加（埋め込み付き）
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids,
                embeddings=[emb if isinstance(emb, list) else emb.tolist() for emb in embeddings]
            )
            
            logger.info(f"ドキュメント '{filename}' をRAGシステムに追加しました（{len(chunks)}チャンク）")
            return True
            
        except Exception as e:
            logger.error(f"ドキュメント追加エラー '{filename}': {str(e)}")
            return False
    
    async def remove_document(self, filename: str) -> bool:
        """ドキュメントをRAGシステムから削除"""
        try:
            # メタデータで直接削除
            self.collection.delete(where={"filename": filename})
            logger.info(f"ドキュメント '{filename}' のチャンクを削除しました")
            
            return True
            
        except Exception as e:
            logger.error(f"ドキュメント削除エラー '{filename}': {str(e)}")
            return False
    
    async def search(self, query: str, n_results: int = 10) -> List[SearchResult]:
        """クエリで検索"""
        try:
            # クエリを埋め込みベクトルに変換
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # コレクションで検索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # 結果を整形
            search_results = []
            if results['documents'] and results['metadatas'] and results['distances']:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # 距離をスコアに変換（距離が小さいほどスコアが高い）
                    score = 1.0 / (1.0 + distance)
                    
                    search_results.append(SearchResult(
                        filename=metadata.get('filename', 'unknown'),
                        content=doc,
                        score=score,
                        metadata=metadata
                    ))
            
            # スコアでソート
            search_results.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"検索クエリ '{query}' で {len(search_results)} 件の結果を取得しました")
            return search_results
            
        except Exception as e:
            logger.error(f"検索エラー: {str(e)}")
            return []
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """テキストをチャンクに分割"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # チャンクの境界を調整（単語の境界で分割）
            if end < len(text):
                # 次の単語の境界を探す
                while end < len(text) and text[end] != ' ' and text[end] != '\n':
                    end += 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # オーバーラップを考慮して次の開始位置を設定
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """コレクション情報を取得"""
        try:
            count = self.collection.count()
            
            # ファイル別の統計情報
            results = self.collection.query(
                query_texts=[""],
                n_results=1000
            )
            
            file_stats = {}
            if results['metadatas']:
                for metadata in results['metadatas'][0]:
                    filename = metadata.get('filename', 'unknown')
                    if filename not in file_stats:
                        file_stats[filename] = {
                            'chunks': 0,
                            'total_size': 0
                        }
                    file_stats[filename]['chunks'] += 1
                    file_stats[filename]['total_size'] += metadata.get('chunk_size', 0)
            
            return {
                "total_documents": count,
                "files": len(file_stats),
                "file_statistics": file_stats
            }
            
        except Exception as e:
            logger.error(f"コレクション情報取得エラー: {str(e)}")
            return {}
    
    async def clear_collection(self) -> bool:
        """コレクションをクリア"""
        try:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "スキルシートのRAG検索用コレクション"}
            )
            logger.info("コレクションをクリアしました")
            return True
            
        except Exception as e:
            logger.error(f"コレクションクリアエラー: {str(e)}")
            return False
