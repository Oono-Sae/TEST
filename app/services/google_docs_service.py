import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import json

from ..config import settings
from ..models.skillsheet import SkillsheetResponse

logger = logging.getLogger(__name__)

class GoogleDocsService:
    """Google Docs連携サービス"""
    
    # Google Drive API スコープ
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/documents.readonly'
    ]
    
    def __init__(self):
        self.creds = None
        self.drive_service = None
        self.docs_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Google API認証"""
        try:
            # トークンファイルのパス
            token_path = Path("token.json")
            credentials_path = Path("credentials.json")
            
            # 既存のトークンがある場合は読み込み
            if token_path.exists():
                self.creds = Credentials.from_authorized_user_file(
                    str(token_path), self.SCOPES
                )
            
            # 有効な認証情報がない場合
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not credentials_path.exists():
                        logger.warning("credentials.json が見つかりません。Google Cloud Consoleからダウンロードしてください。")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # トークンを保存
                with open(token_path, 'w') as token:
                    token.write(self.creds.to_json())
            
            # サービスを初期化
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            
            logger.info("Google API認証が完了しました")
            
        except Exception as e:
            logger.error(f"Google API認証エラー: {str(e)}")
            self.creds = None
    
    async def list_skillsheets(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """スキルシートファイル一覧を取得"""
        try:
            if not self.drive_service:
                logger.warning("Google Drive APIが利用できません")
                return []
            
            # 検索クエリ
            query = "mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='application/pdf'"
            
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            # ファイル一覧を取得
            results = self.drive_service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Google Driveから {len(files)} 件のファイルを取得しました")
            
            return files
            
        except Exception as e:
            logger.error(f"Google Driveファイル一覧取得エラー: {str(e)}")
            return []
    
    async def download_file(self, file_id: str, filename: str) -> Optional[Path]:
        """Google Driveからファイルをダウンロード
        - Google Docs/Sheets/Slides などは export でダウンロード
        - 通常ファイルは get_media でダウンロード
        """
        try:
            if not self.drive_service:
                logger.warning("Google Drive APIが利用できません")
                return None
            
            # ファイル情報を取得
            file = self.drive_service.files().get(fileId=file_id, fields="id, name, mimeType").execute()
            
            # 一時ファイルに保存
            temp_dir = Path(tempfile.gettempdir()) / "skillsheet_rag"
            temp_dir.mkdir(exist_ok=True)
            
            temp_file = temp_dir / filename

            # Google Docs系は exportMimeType を指定
            export_map = {
                'application/vnd.google-apps.document': 'application/pdf',  # Google Docs → PDF
                'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Google Sheets → XLSX
            }

            request = None
            if file.get('mimeType') in export_map:
                request = self.drive_service.files().export_media(fileId=file_id, mimeType=export_map[file['mimeType']])
                # 拡張子を補正
                if file['mimeType'] == 'application/vnd.google-apps.document' and not filename.lower().endswith('.pdf'):
                    temp_file = temp_dir / (Path(filename).stem + '.pdf')
                if file['mimeType'] == 'application/vnd.google-apps.spreadsheet' and not filename.lower().endswith('.xlsx'):
                    temp_file = temp_dir / (Path(filename).stem + '.xlsx')
            else:
                # 通常ファイルのバイナリ取得
                request = self.drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"ダウンロード進捗: {int(status.progress() * 100)}%")
            
            # ファイルに保存
            with open(temp_file, 'wb') as f:
                f.write(fh.getvalue())
            
            logger.info(f"ファイルダウンロード完了: {filename}")
            return temp_file
            
        except Exception as e:
            logger.error(f"ファイルダウンロードエラー: {str(e)}")
            return None
    
    async def get_document_content(self, document_id: str) -> Optional[str]:
        """Google Docsの内容を取得"""
        try:
            if not self.docs_service:
                logger.warning("Google Docs APIが利用できません")
                return None
            
            # ドキュメントの内容を取得
            document = self.docs_service.documents().get(documentId=document_id).execute()
            
            # テキスト内容を抽出
            content = []
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for para_element in element['paragraph']['elements']:
                        if 'textRun' in para_element:
                            content.append(para_element['textRun']['content'])
            
            text_content = ''.join(content)
            logger.info(f"Google Docs内容取得完了: {len(text_content)} 文字")
            
            return text_content
            
        except Exception as e:
            logger.error(f"Google Docs内容取得エラー: {str(e)}")
            return None
    
    async def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Google Driveでファイルを検索"""
        try:
            if not self.drive_service:
                logger.warning("Google Drive APIが利用できません")
                return []
            
            # ファイル名で検索
            search_query = f"name contains '{query}' and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='application/pdf')"
            
            results = self.drive_service.files().list(
                q=search_query,
                pageSize=50,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Google Drive検索結果: {len(files)} 件")
            
            return files
            
        except Exception as e:
            logger.error(f"Google Drive検索エラー: {str(e)}")
            return []
    
    def is_authenticated(self) -> bool:
        """認証状態を確認"""
        return self.creds is not None and self.creds.valid
