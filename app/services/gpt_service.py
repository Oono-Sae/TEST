import openai
import logging
from typing import List, Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class GPTService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
        if self.api_key:
            openai.api_key = self.api_key
            logger.info(f"GPTサービスを初期化しました: {self.model}")
        else:
            logger.warning("OpenAI APIキーが設定されていません")
    
    async def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> Optional[str]:
        """GPTを使用して質問に対する回答を生成"""
        if not self.api_key:
            logger.error("OpenAI APIキーが設定されていません")
            return None
        
        try:
            # コンテキストを構築
            context_text = self._build_context(context)
            
            # プロンプトを作成
            system_prompt = """あなたはスキルシートの専門家です。与えられたコンテキストに基づいて、質問に対する詳細で正確な回答を提供してください。

回答の際は以下の点に注意してください：
1. コンテキストに含まれる情報のみを使用する
2. 具体的な例や詳細を含める
3. 専門的で分かりやすい説明を心がける
4. 日本語で回答する

コンテキストに情報がない場合は、「申し訳ございませんが、提供された情報からは回答できません」と明記してください。"""

            user_prompt = f"""コンテキスト情報：
{context_text}

質問：{query}

上記のコンテキストに基づいて、質問に対する詳細な回答を提供してください。"""

            # GPT APIを呼び出し
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            answer = response.choices[0].message.content
            logger.info(f"GPT回答を生成しました: {len(answer)}文字")
            return answer
            
        except Exception as e:
            logger.error(f"GPT回答生成エラー: {str(e)}")
            return None
    
    def _build_context(self, context: List[Dict[str, Any]]) -> str:
        """検索結果のコンテキストを構築"""
        context_parts = []
        
        for i, item in enumerate(context, 1):
            filename = item.get('filename', '不明なファイル')
            content = item.get('content', '')
            score = item.get('score', 0)
            
            context_part = f"""
--- 情報 {i} ---
ファイル: {filename}
類似度スコア: {score:.3f}
内容: {content}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def is_available(self) -> bool:
        """GPTサービスが利用可能かチェック"""
        return bool(self.api_key)
