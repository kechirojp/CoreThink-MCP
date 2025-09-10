"""
CoreThink-MCP Elicitation Handler Implementation
FastMCP 2.10.0+ の User Elicitation 機能を実装

Elicitation 機能:
- サーバーがツール実行中にユーザーに追加情報を要求
- 不完全な入力でも段階的に情報収集して実行可能
- CoreThink-MCP の自然言語推論と組み合わせて高度なUX実現
"""

from typing import Any, Dict, Optional, Type, Union
import logging
from dataclasses import dataclass
from fastmcp.client.elicitation import ElicitResult

logger = logging.getLogger(__name__)

@dataclass
class ElicitationContext:
    """Elicitation のコンテキスト情報"""
    tool_name: str
    current_params: Dict[str, Any]
    missing_params: list[str]
    reasoning_context: Optional[str] = None

class CoreThinkElicitationHandler:
    """
    CoreThink-MCP専用のElicitationハンドラー
    
    自然言語推論と組み合わせて、ユーザーとの対話的な情報収集を実現:
    - 不足パラメータの自動検出
    - 文脈に応じた質問生成
    - GSR推論による適切な情報要求
    """
    
    def __init__(self):
        self.conversation_history: list[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        
    async def handle_elicitation(
        self,
        message: str,
        response_type: Type,
        params: Any,
        context: Any
    ) -> Union[Any, ElicitResult]:
        """
        Elicitation リクエストを処理
        
        Args:
            message: サーバーからのメッセージ
            response_type: 期待される応答型
            params: リクエストパラメータ
            context: リクエストコンテキスト
            
        Returns:
            構造化された応答データまたはElicitResult
        """
        logger.info(f"Elicitation要求: {message}")
        
        try:
            # CoreThink-MCP固有のコンテキスト分析
            elicit_context = self._analyze_elicitation_context(message, params, context)
            
            # 自然言語での質問生成
            enhanced_message = self._enhance_question_with_reasoning(message, elicit_context)
            
            # ユーザーインタラクション
            user_input = await self._get_user_input(enhanced_message, response_type)
            
            if user_input is None:
                return ElicitResult(action="decline")
                
            # 応答の構造化と検証
            structured_response = self._structure_response(user_input, response_type, elicit_context)
            
            # 会話履歴の更新
            self._update_conversation_history(message, user_input, elicit_context)
            
            logger.info("Elicitation応答完了")
            return structured_response
            
        except Exception as e:
            logger.error(f"Elicitation処理エラー: {str(e)}")
            return ElicitResult(action="cancel")
    
    def _analyze_elicitation_context(
        self, 
        message: str, 
        params: Any, 
        context: Any
    ) -> ElicitationContext:
        """Elicitationのコンテキストを分析"""
        
        # ツール名の推定（コンテキストから）
        tool_name = getattr(context, 'tool_name', 'unknown')
        
        # 現在のパラメータ状況
        current_params = getattr(params, 'currentParams', {})
        
        # 不足パラメータの特定
        missing_params = self._identify_missing_params(message, params)
        
        # 推論コンテキストの構築
        reasoning_context = self._build_reasoning_context(tool_name, current_params)
        
        return ElicitationContext(
            tool_name=tool_name,
            current_params=current_params,
            missing_params=missing_params,
            reasoning_context=reasoning_context
        )
    
    def _enhance_question_with_reasoning(
        self, 
        original_message: str, 
        elicit_context: ElicitationContext
    ) -> str:
        """CoreThink-MCP の推論機能で質問を強化 - より自然な対話を実現"""
        
        # ツール別の自然な文脈メッセージ
        tool_contexts = {
            'reason_about_change': '🤔 変更内容を詳しく検討しています...',
            'validate_against_constraints': '🔍 安全性を確認しています...',
            'execute_with_safeguards': '⚡ 実行準備を進めています...',
            'refine_understanding': '💭 理解を深めています...',
            'trace_reasoning_steps': '🧠 推論プロセスを分析しています...'
        }
        
        context_intro = tool_contexts.get(elicit_context.tool_name, '🔄 処理を続行しています...')
        
        # より自然で会話的なメッセージに変換
        enhanced_message = f"""{context_intro}

{original_message}

💡 この情報により、より適切で安全な処理が可能になります。

📝 回答のヒント:
• 具体的で実行可能な内容をお答えください
• 不明な場合は「不明」または「後で」と入力
• 全体をキャンセルしたい場合は「cancel」と入力

あなたの回答:"""
        
        return enhanced_message.strip()
    
    async def _get_user_input(
        self, 
        enhanced_message: str, 
        response_type: Type
    ) -> Optional[str]:
        """ユーザーからの入力を取得 - セッション違和感を最小化"""
        
        # セッション継続性を保つための自然な表示
        print("\n" + "─" * 60)
        print("🤖 AI Assistant からの確認")
        print("─" * 60)
        print(enhanced_message)
        print("─" * 60)
        
        try:
            # ユーザー入力の取得
            user_input = input("💬 ").strip()
            
            # キャンセル・スキップの判定
            if user_input.lower() in ['cancel', 'キャンセル', 'quit', 'exit']:
                print("❌ 処理をキャンセルしました。")
                return None
            elif user_input.lower() in ['skip', 'スキップ', '不明', '後で', 'unknown']:
                print("⏭️ この項目をスキップします。")
                return ""
            elif not user_input:
                print("ℹ️ 空の回答のため、スキップします。")
                return ""
            
            print(f"✅ 回答を受け付けました: {user_input}")
            return user_input
            
        except (EOFError, KeyboardInterrupt):
            print("\n❌ 入力がキャンセルされました。")
            return None
    
    def _structure_response(
        self, 
        user_input: str, 
        response_type: Type, 
        elicit_context: ElicitationContext
    ) -> Any:
        """ユーザー入力を適切な形式に構造化"""
        
        if response_type is None:
            # 空オブジェクトが期待される場合
            return {}
        
        # 基本的な構造化（response_typeに基づいて）
        if hasattr(response_type, '__dataclass_fields__'):
            # データクラスの場合
            fields = response_type.__dataclass_fields__
            
            if 'value' in fields:
                return response_type(value=user_input)
            elif len(fields) == 1:
                field_name = list(fields.keys())[0]
                return response_type(**{field_name: user_input})
            else:
                # 複数フィールドの場合は基本値で初期化
                kwargs = {}
                for field_name, field in fields.items():
                    if field_name.lower() in ['value', 'input', 'text', 'content']:
                        kwargs[field_name] = user_input
                    else:
                        kwargs[field_name] = self._get_default_value(field.type)
                return response_type(**kwargs)
        
        # フォールバック: 辞書形式
        return {"value": user_input}
    
    def _identify_missing_params(self, message: str, params: Any) -> list[str]:
        """不足パラメータを特定"""
        missing = []
        
        # メッセージからパラメータ名を推定
        common_params = [
            'user_intent', 'current_state', 'proposed_action',
            'ambiguous_request', 'context_clues', 'domain_hints',
            'task_description', 'repository_path', 'target_issue'
        ]
        
        for param in common_params:
            if param.replace('_', ' ') in message.lower():
                missing.append(param)
        
        return missing
    
    def _build_reasoning_context(
        self, 
        tool_name: str, 
        current_params: Dict[str, Any]
    ) -> str:
        """推論コンテキストを構築"""
        
        tool_contexts = {
            'reason_about_change': '変更提案の安全性と妥当性を評価するための情報',
            'validate_against_constraints': '制約適合性を検証するための詳細情報',
            'execute_with_safeguards': '安全な実行のための実行計画情報',
            'refine_understanding': '曖昧性解消のための文脈情報',
            'trace_reasoning_steps': '推論過程の詳細度調整情報'
        }
        
        base_context = tool_contexts.get(tool_name, 'ツール実行のための補足情報')
        
        if current_params:
            param_info = f"既存パラメータ: {', '.join(current_params.keys())}"
            return f"{base_context}\n{param_info}"
        
        return base_context
    
    def _get_default_value(self, field_type: Type) -> Any:
        """型に基づいてデフォルト値を取得"""
        if field_type == str:
            return ""
        elif field_type == int:
            return 0
        elif field_type == bool:
            return False
        elif field_type == list:
            return []
        elif field_type == dict:
            return {}
        else:
            return None
    
    def _update_conversation_history(
        self, 
        question: str, 
        answer: str, 
        context: ElicitationContext
    ):
        """会話履歴を更新"""
        
        self.conversation_history.append({
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'tool': context.tool_name,
            'question': question,
            'answer': answer,
            'context': context.reasoning_context
        })
        
        # 履歴のサイズ制限（最新100件）
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]

# グローバルインスタンス
corethink_elicitation_handler = CoreThinkElicitationHandler()

# FastMCP Client で使用するためのハンドラー関数
async def elicitation_handler(
    message: str,
    response_type: Type,
    params: Any,
    context: Any
) -> Union[Any, ElicitResult]:
    """FastMCP Client 用のElicitationハンドラー"""
    return await corethink_elicitation_handler.handle_elicitation(
        message, response_type, params, context
    )
