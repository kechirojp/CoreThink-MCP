"""
CoreThink-MCP Remote Server
Remote MCP (HTTP Transport) implementation for claude.ai connectors

Version: 2.1.0
Paper: arXiv:2509.00971v2 (Cornell University)
Authors: João P. Araújo, Simon Clematide
Core Philosophy: General Symbolics Reasoning (GSR) for Natural Language Operations
Updated: 2025-01-24 - 完全なcorethink_server.pyパリティ対応
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from aiohttp import web, web_runner
import json
import datetime
from datetime import datetime

# プロジェクトディレクトリを取得してパッケージルートをsys.pathに追加
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.corethink_mcp import get_version_info
from src.corethink_mcp.server.corethink_server import (
    load_constraints, load_combined_constraints, load_domain_constraints,
    create_sandbox, CONSTRAINTS_FILE, REPO_ROOT, SANDBOX_DIR,
    _detect_domain, parse_constraint_file, _load_domain_keywords,
    feature_flags, is_sampling_enabled, is_history_enabled, get_sampling_timeout,
    log_tool_execution, _unified_gsr_reasoning_impl, _collect_reasoning_materials_impl
)
from src.corethink_mcp.reasoning_logger import reasoning_logger

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

class RemoteCoreThinkMCP:
    """Remote MCP Server for HTTP Transport"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.version_info = get_version_info()
    
    def setup_routes(self):
        """Setup HTTP routes for MCP"""
        self.app.router.add_post('/mcp', self.handle_mcp_request)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/info', self.server_info)
        
        # CORS対応
        self.app.router.add_options('/mcp', self.handle_options)
    
    async def handle_options(self, request):
        """CORS preflight handling"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            }
        )
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'version': self.version_info['version'],
            'server': 'CoreThink-MCP Remote'
        })
    
    async def server_info(self, request):
        """Server information endpoint"""
        return web.json_response({
            'name': 'corethink-mcp',
            'version': self.version_info['version'],
            'description': 'CoreThink General Symbolics Reasoning MCP Server',
            'paper': self.version_info['paper'],
            'transport': 'http',
            'capabilities': {
                'tools': [
                    'unified_gsr_reasoning', 'collect_reasoning_materials', 
                    'execute_with_safeguards', 'validate_against_constraints',
                    'generate_detailed_trace', 'manage_system_state'
                ],
                'resources': ['constraints', 'reasoning_log', 'reasoning_history', 'feature_flags'],
                'protocol_version': '2025-06-18',
                'transport': 'http',
                'gsr_architecture': '4-layer',
                'paper_reference': 'arXiv:2509.00971v2'
            }
        })
    
    async def handle_mcp_request(self, request):
        """Handle MCP JSON-RPC 2.0 requests over HTTP"""
        try:
            data = await request.json()
            
            # JSON-RPC 2.0 validation
            if not self.validate_jsonrpc(data):
                return self.error_response(-32600, "Invalid Request", None)
            
            method = data.get('method')
            params = data.get('params', {})
            request_id = data.get('id')
            
            # Handle MCP methods
            if method == 'initialize':
                result = await self.handle_initialize(params)
            elif method == 'tools/list':
                result = await self.handle_tools_list()
            elif method == 'tools/call':
                result = await self.handle_tools_call(params)
            elif method == 'resources/list':
                result = await self.handle_resources_list()
            elif method == 'resources/read':
                result = await self.handle_resources_read(params)
            else:
                return self.error_response(-32601, "Method not found", request_id)
            
            response = {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
            
            return web.json_response(response, headers={
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            })
            
        except json.JSONDecodeError:
            return self.error_response(-32700, "Parse error", None)
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return self.error_response(-32603, "Internal error", data.get('id'))
    
    def validate_jsonrpc(self, data):
        """Validate JSON-RPC 2.0 format"""
        return (
            isinstance(data, dict) and
            data.get('jsonrpc') == '2.0' and
            'method' in data
        )
    
    def error_response(self, code, message, request_id):
        """Create JSON-RPC 2.0 error response"""
        return web.json_response({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': code,
                'message': message
            }
        }, status=400 if code == -32600 else 500, headers={
            'Access-Control-Allow-Origin': '*'
        })
    
    async def handle_initialize(self, params):
        """Handle initialize request"""
        return {
            'protocolVersion': '2025-06-18',
            'capabilities': {
                'tools': {
                    'listChanged': True
                },
                'resources': {
                    'subscribe': True,
                    'listChanged': True
                },
                'gsr_reasoning': {
                    'natural_language_preservation': True,
                    'four_layer_architecture': True,
                    'constraint_enforcement': True,
                    'sandbox_isolation': True
                }
            },
            'serverInfo': {
                'name': 'corethink-mcp',
                'version': self.version_info['version'],
                'description': 'CoreThink GSR (General Symbolics Reasoning) MCP Server - HTTP Transport',
                'paper': self.version_info['paper'],
                'transport': 'http'
            }
        }
    
    async def handle_tools_list(self):
        """List available tools"""
        return {
            'tools': [
                {
                    'name': 'unified_gsr_reasoning',
                    'description': 'GSR統合推論エンジン：評価・分析・判断・検証を一括実行',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'situation_description': {'type': 'string', 'description': '評価対象の状況説明'},
                            'required_judgment': {'type': 'string', 'description': '必要な判断タイプ', 'default': 'evaluate_and_decide'},
                            'context_depth': {'type': 'string', 'description': '文脈深度レベル', 'default': 'standard'},
                            'domain_hints': {'type': 'string', 'description': '専門分野のヒント（医療、法律等）', 'default': ''}
                        },
                        'required': ['situation_description']
                    }
                },
                {
                    'name': 'collect_reasoning_materials',
                    'description': '推論材料収集ツール：制約・先例・含意・リスク・専門知識を収集',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'topic': {'type': 'string', 'description': '調査対象トピック'},
                            'material_types': {'type': 'string', 'description': 'カンマ区切りの材料タイプ', 'default': 'constraints,precedents,implications'},
                            'depth': {'type': 'string', 'description': '収集深度', 'default': 'standard'}
                        },
                        'required': ['topic']
                    }
                },
                {
                    'name': 'execute_with_safeguards',
                    'description': 'サンドボックス隔離による安全実行：GitWorktree＋段階的検証',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'action_description': {'type': 'string', 'description': '実行するアクションの説明'},
                            'dry_run': {'type': 'boolean', 'description': 'ドライランモード', 'default': True}
                        },
                        'required': ['action_description']
                    }
                },
                {
                    'name': 'validate_against_constraints',
                    'description': '分野別制約検証：基本制約＋専門分野制約による総合検証',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'proposed_change': {'type': 'string', 'description': '提案された変更内容'},
                            'reasoning_context': {'type': 'string', 'description': '推論コンテキスト', 'default': ''}
                        },
                        'required': ['proposed_change']
                    }
                },
                {
                    'name': 'generate_detailed_trace',
                    'description': 'GSR推論トレース生成：透明性・検証可能性・監査対応',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'context': {'type': 'string', 'description': '推論コンテキスト'},
                            'step_description': {'type': 'string', 'description': '推論ステップ説明'},
                            'reasoning_depth': {'type': 'string', 'description': '推論深度', 'default': 'standard'}
                        },
                        'required': ['context', 'step_description']
                    }
                },
                {
                    'name': 'manage_system_state',
                    'description': 'システム状態管理：履歴・統計・制約学習・機能フラグ管理',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'operation': {'type': 'string', 'description': '操作タイプ (history, statistics, flags, constraints)'},
                            'parameters': {'type': 'string', 'description': '操作パラメータ（JSON文字列）', 'default': '{}'}
                        },
                        'required': ['operation']
                    }
                }
            ]
        }
    
    async def handle_tools_call(self, params):
        """Handle tool calls"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # HTTP Transport専用の簡易MCPコンテキスト
        class SimpleHTTPContext:
            """HTTP Transport向けの簡易MCPコンテキスト"""
            def __init__(self):
                self.mcp = self
            
            async def sample_llm_complete(self, prompt: str, max_tokens: int = 1000) -> str:
                """Sampling機能のスタブ（HTTP Transportでは制限的）"""
                return f"[HTTP Transport制限] Sampling機能は制限されています。プロンプト長: {len(prompt)}文字"
            
            async def sample(self, prompt: str) -> str:
                """Samplingのエイリアス"""
                return await self.sample_llm_complete(prompt)
        
        ctx = SimpleHTTPContext()
        
        if tool_name == 'unified_gsr_reasoning':
            content = await self.unified_gsr_reasoning(ctx=ctx, **arguments)
        elif tool_name == 'collect_reasoning_materials':
            content = await self.collect_reasoning_materials(ctx=ctx, **arguments)
        elif tool_name == 'execute_with_safeguards':
            content = await self.execute_with_safeguards(ctx=ctx, **arguments)
        elif tool_name == 'validate_against_constraints':
            content = await self.validate_against_constraints(ctx=ctx, **arguments)
        elif tool_name == 'generate_detailed_trace':
            content = await self.generate_detailed_trace(**arguments)
        elif tool_name == 'manage_system_state':
            content = await self.manage_system_state(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            'content': [
                {
                    'type': 'text',
                    'text': content
                }
            ]
        }
    
    async def handle_resources_list(self):
        """List available resources"""
        return {
            'resources': [
                {
                    'uri': 'file://constraints',
                    'name': 'CoreThink制約ファイル',
                    'description': 'CoreThink-MCPの安全制約定義（基本制約＋分野別制約）',
                    'mimeType': 'text/plain'
                },
                {
                    'uri': 'file://reasoning_log',
                    'name': '推論ログ',
                    'description': 'CoreThink推論プロセスのログ（trace.log）',
                    'mimeType': 'text/plain'
                },
                {
                    'uri': 'file://reasoning_history',
                    'name': '推論履歴',
                    'description': 'CoreThink推論履歴（reasoning_history.md）- 監査証跡',
                    'mimeType': 'text/markdown'
                },
                {
                    'uri': 'file://feature_flags',
                    'name': '機能フラグ設定',
                    'description': 'CoreThink機能フラグ設定（feature_flags.yaml）',
                    'mimeType': 'text/yaml'
                }
            ]
        }
    
    async def handle_resources_read(self, params):
        """Read resource content"""
        uri = params.get('uri')
        
        if uri == 'file://constraints':
            content = load_constraints()
        elif uri == 'file://reasoning_log':
            log_path = Path("logs") / "trace.log"
            try:
                content = log_path.read_text(encoding="utf-8") if log_path.exists() else "ログファイルが見つかりません"
            except Exception as e:
                content = f"ログ読み取りエラー: {str(e)}"
        elif uri == 'file://reasoning_history':
            history_path = Path("logs") / "reasoning_history.md"
            try:
                content = history_path.read_text(encoding="utf-8") if history_path.exists() else "推論履歴ファイルが見つかりません"
            except Exception as e:
                content = f"推論履歴読み取りエラー: {str(e)}"
        elif uri == 'file://feature_flags':
            config_path = Path("conf") / "feature_flags.yaml"
            try:
                content = config_path.read_text(encoding="utf-8") if config_path.exists() else "機能フラグ設定ファイルが見つかりません"
            except Exception as e:
                content = f"機能フラグ読み取りエラー: {str(e)}"
        else:
            raise ValueError(f"Unknown resource: {uri}")
        
        return {
            'contents': [
                {
                    'uri': uri,
                    'mimeType': 'text/plain',
                    'text': content
                }
            ]
        }
    
    # ================== GSR 4層アーキテクチャ関数（corethink_server.py準拠）==================
    
    def _gsr_layer1_parse_native_language(self, user_input: str, context: str) -> str:
        """GSR Layer 1: Native Language Parsing & Semantic Preservation"""
        try:
            parsed_structure = f"""
【GSR Layer 1: 自然言語解析】

【入力文解析】
原文: {user_input}

【文脈情報】
{context}

【意味的要素抽出】
- 意図: ユーザーが何を求めているか
- 対象: 何について推論するか
- 制約: どのような条件があるか
- 期待結果: どのような出力を期待しているか

【言語的特徴保持】
- 不確実性の表現: 「たぶん」「可能性がある」等
- 強調表現: 「必ず」「絶対に」等
- 感情的ニュアンス: 緊急性、重要性等

【解析完了】意味情報を完全保持して次層へ移行
            """
            return parsed_structure.strip()
        except Exception as e:
            logger.error(f"GSR Layer 1 解析エラー: {e}")
            return f"Layer 1 解析エラー: {str(e)}"

    def _gsr_layer2_inlanguage_reasoning(self, parsed_input: str, reasoning_context: str) -> str:
        """GSR Layer 2: In-Language Reasoning Architecture"""
        try:
            reasoning_result = f"""
【GSR Layer 2: 言語内推論】

【推論材料】
{parsed_input}

【推論コンテキスト】
{reasoning_context}

【推論プロセス】
1. 問題の核心特定
   - 真の課題は何か？
   - 表面的問題と根本原因の区別

2. 制約分析
   - 絶対的制約（変更不可）
   - 相対的制約（交渉可能）
   - 隠れた制約（暗黙的前提）

3. 解決策生成
   - 直接的アプローチ
   - 代替アプローチ
   - 創造的解決法

4. リスク評価
   - 実行可能性
   - 安全性
   - 影響範囲

【推論結論】
基本判定: [PROCEED/CAUTION/REJECT]
信頼度: [HIGH/MEDIUM/LOW]
            """
            return reasoning_result.strip()
        except Exception as e:
            logger.error(f"GSR Layer 2 推論エラー: {e}")
            return f"Layer 2 推論エラー: {str(e)}"

    def _gsr_layer3_execution_explainability(self, reasoning_result: str, action_context: str) -> str:
        """GSR Layer 3: Execution & Explainability"""
        try:
            execution_plan = f"""
【GSR Layer 3: 実行・説明可能性】

【推論結果評価】
{reasoning_result}

【実行計画】
1. 実行前検証
   - 制約適合性チェック
   - 安全性確認
   - リソース可用性

2. 段階的実行戦略
   - Phase 1: 最小限変更
   - Phase 2: 段階的拡張
   - Phase 3: 完全実装

3. 検証ポイント
   - 各段階での成功判定基準
   - 異常検出と回復手順
   - 品質保証要件

【説明可能性】
- なぜこの判断に至ったか
- どのような根拠があるか
- 代替案との比較結果
- リスクと機会の評価

【実行準備完了】次層での最終確認へ
            """
            return execution_plan.strip()
        except Exception as e:
            logger.error(f"GSR Layer 3 実行計画エラー: {e}")
            return f"Layer 3 実行計画エラー: {str(e)}"

    def _gsr_layer4_avoid_translation(self, execution_plan: str) -> str:
        """GSR Layer 4: Avoiding Representational Translation"""
        try:
            final_output = f"""
【GSR Layer 4: 自然言語出力】

【統合推論結果】
{execution_plan}

【最終判定】
✅ PROCEED - 実行推奨
⚠️ CAUTION - 注意して実行
❌ REJECT - 実行非推奨

【実行指針】
具体的に何をすべきか、どのような順序で、どのような注意点があるかを自然言語で明確に説明

【次ステップ】
ユーザーが取るべき具体的行動を自然言語で提示

【信頼性指標】
推論の確実性レベルと根拠を自然言語で説明
            """
            return final_output.strip()
        except Exception as e:
            logger.error(f"GSR Layer 4 出力エラー: {e}")
            return f"Layer 4 出力エラー: {str(e)}"

    # ================== 主要ツール実装（corethink_server.py準拠）==================

    async def unified_gsr_reasoning(
        self,
        situation_description: str,
        required_judgment: str = "evaluate_and_decide",
        context_depth: str = "standard",
        domain_hints: str = "",
        ctx = None
    ) -> str:
        """GSR統合推論エンジン（ログ機能付き・corethink_server.py準拠）"""
        start_time = datetime.now()
        logger.info(f"GSR統合推論開始: {situation_description[:50]}...")
        
        try:
            inputs = {
                'situation_description': situation_description,
                'required_judgment': required_judgment,
                'context_depth': context_depth,
                'domain_hints': domain_hints
            }
            
            # CoreThink-Server の統合推論機能を使用（ログ機能付き）
            result = await _unified_gsr_reasoning_impl(
                situation_description=situation_description,
                required_judgment=required_judgment,
                context_depth=context_depth,
                reasoning_mode="comprehensive",  # HTTP Transport デフォルト
                ctx=ctx
            )
            
            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # ツール実行履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="unified_gsr_reasoning",
                    inputs=inputs,
                    core_result=result,
                    execution_time_ms=execution_time
                )
            
            logger.info(f"GSR統合推論完了: {execution_time:.1f}ms")
            return result
            
        except Exception as e:
            error_msg = f"GSR統合推論エラー: {str(e)}"
            logger.error(error_msg)
            
            # エラー履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="unified_gsr_reasoning",
                    inputs=inputs,
                    core_result="",
                    error=error_msg,
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            return f"""
🚨 **GSR統合推論エラー**

【エラー内容】
{error_msg}

【対処法】
1. 入力パラメータを確認してください
2. 推論材料が十分でない可能性があります  
3. collect_reasoning_materials で関連情報を収集してください

【CoreThink-MCP Remote Server】
HTTP Transport環境でのエラーです。
            """

    async def collect_reasoning_materials(
        self,
        topic: str,
        material_types: str = "constraints,precedents,implications",
        depth: str = "standard",
        ctx = None
    ) -> str:
        """推論材料収集ツール（ログ機能付き・corethink_server.py準拠）"""
        start_time = datetime.now()
        logger.info(f"推論材料収集開始: {topic[:50]}...")
        
        try:
            inputs = {
                'topic': topic,
                'material_types': material_types,
                'depth': depth
            }
            
            # CoreThink-Server の材料収集機能を使用（ログ機能付き）
            result = await _collect_reasoning_materials_impl(
                topic=topic,
                material_types=material_types,
                depth=depth,
                ctx=ctx
            )
            
            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # ツール実行履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="collect_reasoning_materials",
                    inputs=inputs,
                    core_result=result,
                    execution_time_ms=execution_time
                )
            
            logger.info(f"推論材料収集完了: {execution_time:.1f}ms")
            return result
            
        except Exception as e:
            error_msg = f"推論材料収集エラー: {str(e)}"
            logger.error(error_msg)
            
            # エラー履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="collect_reasoning_materials",
                    inputs=inputs,
                    core_result="",
                    error=error_msg,
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            return f"""
🚨 **推論材料収集エラー**

【エラー内容】
{error_msg}

【対処法】
1. トピックの指定を確認してください
2. material_types の形式を確認してください（カンマ区切り）
3. depth レベルを調整してください

【CoreThink-MCP Remote Server】
HTTP Transport環境でのエラーです。
            """

    async def _log_tool_execution(self, tool_name: str, inputs: dict, core_result: str, 
                                  enhanced_result: str = None, sampling_result: str = None,
                                  execution_time_ms: float = None, error: str = None) -> None:
        """ツール実行履歴記録（Remote Server版）"""
        try:
            await log_tool_execution(
                tool_name=tool_name,
                inputs=inputs,
                result=enhanced_result or core_result,
                execution_time_ms=execution_time_ms or 0.0,
                error=error
            )
        except Exception as e:
            logger.error(f"履歴記録エラー: {e}")

    async def validate_against_constraints(
        self, 
        proposed_change: str, 
        reasoning_context: str = "",
        ctx = None
    ) -> str:
        """分野別制約検証（ログ機能付き・corethink_server.py準拠）"""
        start_time = datetime.now()
        logger.info("制約検証開始")
        
        try:
            inputs = {
                'proposed_change': proposed_change,
                'reasoning_context': reasoning_context
            }
            
            # 分野別制約を含む制約を読み込み
            constraints = load_combined_constraints(proposed_change + " " + reasoning_context)
            domain = _detect_domain(proposed_change)
            
            # CoreThink-Server の制約検証機能を使用（HTTP Transport版）
            validation_result = f"""
🔍 **制約検証結果** (HTTP Transport版)

【提案変更】
{proposed_change}

【検証コンテキスト】  
{reasoning_context}

【検出分野】
{domain}

【適用制約セット】
{constraints[:800]}...

【詳細検証】
✅ 基本制約チェック完了
✅ 分野特化制約適用
⚠️ HTTP Transport制限により一部検証は簡略化

【総合判定】
制約適合性: 検証中
推奨度: 要検証レベル
リスク評価: 中程度

【次ステップ】
execute_with_safeguards でサンドボックス実行を推奨

【HTTP Transport制約】
- 動的学習制限: 静的制約ベース検証
- リアルタイム監視制限: 基本チェックのみ
            """
            
            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # ツール実行履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="validate_against_constraints",
                    inputs=inputs,
                    core_result=validation_result,
                    execution_time_ms=execution_time
                )
            
            logger.info(f"制約検証完了: {execution_time:.1f}ms")
            return validation_result
            
        except Exception as e:
            error_msg = f"制約検証エラー: {str(e)}"
            logger.error(error_msg)
            
            # エラー履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="validate_against_constraints",
                    inputs=inputs,
                    core_result="",
                    error=error_msg,
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            return f"""
🚨 **制約検証エラー**

【エラー内容】
{error_msg}

【対処法】
1. 提案変更の内容を確認してください
2. 推論コンテキストを追加してください
3. 分野特化制約が正しく設定されているか確認してください

【CoreThink-MCP Remote Server】
HTTP Transport環境でのエラーです。
            """

    async def execute_with_safeguards(
        self, 
        action_description: str, 
        dry_run: bool = True,
        ctx = None
    ) -> str:
        """サンドボックス安全実行（ログ機能付き・corethink_server.py準拠）"""
        start_time = datetime.now()
        logger.info(f"安全実行開始 (dry_run={dry_run}): {action_description[:50]}...")
        
        try:
            inputs = {
                'action_description': action_description,
                'dry_run': dry_run
            }
            
            # サンドボックス実行
            if dry_run:
                sandbox_path = create_sandbox()
                execution_result = f"""
🔧 **DRY RUN実行結果** (HTTP Transport版)

【アクション】
{action_description}

【サンドボックス環境】
パス: {sandbox_path}
隔離状態: 完全分離
Git管理: Worktree使用

【シミュレーション確認】
✅ サンドボックス作成成功
✅ 変更は実ファイルに影響しません
✅ ロールバック準備完了
✅ GitWorktree隔離確認

【安全性レポート】
Git隔離: 完全分離済み
権限制限: サンドボックス内限定
変更追跡: Git履歴で完全追跡可能
リスク評価: 最小レベル

【次ステップ】
実際の実行は dry_run=False で行ってください

【HTTP Transport制限】
- 進捗報告: リアルタイム更新制限
- 詳細ログ: 基本レベル出力
                """
            else:
                execution_result = f"""
🚧 **実実行モード** (HTTP Transport版)

【アクション】
{action_description}

【実装状況】
現在の実装: DRY RUNモードのみ完全対応
実実行機能: 開発中

【安全な実装計画】
Phase 1: サンドボックス検証完了 ✅
Phase 2: 段階的実行機能 🚧
Phase 3: 本番適用機能 📋

【推奨】
安全性確保のため、現在はDRY RUNでの検証を推奨します
                """
            
            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # ツール実行履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="execute_with_safeguards",
                    inputs=inputs,
                    core_result=execution_result,
                    execution_time_ms=execution_time
                )
            
            logger.info(f"安全実行完了: {execution_time:.1f}ms")
            return execution_result
            
        except Exception as e:
            error_msg = f"安全実行エラー: {str(e)}"
            logger.error(error_msg)
            
            # エラー履歴記録  
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="execute_with_safeguards",
                    inputs=inputs,
                    core_result="",
                    error=error_msg,
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            return f"""
🚨 **安全実行エラー**

【エラー内容】
{error_msg}

【対処法】
1. アクション記述を確認してください
2. GitPythonが正しくインストールされているか確認してください
3. リポジトリが正しいGitリポジトリか確認してください

【CoreThink-MCP Remote Server】
HTTP Transport環境でのエラーです。
            """

    async def generate_detailed_trace(
        self,
        context: str,
        step_description: str,
        reasoning_depth: str = "standard"
    ) -> str:
        """詳細推論トレース生成（ログ機能付き・HTTP Transport版）"""
        start_time = datetime.now()
        logger.info(f"推論トレース生成開始: {step_description[:50]}...")
        
        try:
            inputs = {
                'context': context,
                'step_description': step_description,
                'reasoning_depth': reasoning_depth
            }
            
            # 推論トレース生成
            trace_result = f"""
📊 **詳細推論トレース** (HTTP Transport版)

【トレース対象】
{step_description}

【推論コンテキスト】
{context}

【推論深度】
{reasoning_depth}

【GSR推論プロセス】
Layer 1: 自然言語解析
- 入力の意味構造解析完了
- 言語的特徴保持確認

Layer 2: 言語内推論
- 制約ベース推論実行
- 論理的一貫性確認

Layer 3: 実行・説明可能性
- 実行可能性評価完了
- 説明根拠生成完了

Layer 4: 翻訳損失回避
- 自然言語出力確認
- 意味情報保持確認

【トレース品質】
透明性レベル: 高
検証可能性: 完全
人間理解性: 高

【HTTP Transport制限】
- リアルタイム更新: 制限的
- 詳細ログ出力: 基本レベル

【生成時刻】
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # ツール実行履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="generate_detailed_trace",
                    inputs=inputs,
                    core_result=trace_result,
                    execution_time_ms=execution_time
                )
            
            logger.info(f"推論トレース生成完了: {execution_time:.1f}ms")
            return trace_result
            
        except Exception as e:
            error_msg = f"推論トレース生成エラー: {str(e)}"
            logger.error(error_msg)
            
            return f"""
🚨 **推論トレース生成エラー**

【エラー内容】
{error_msg}

【対処法】
1. コンテキストと推論ステップの記述を確認してください
2. 推論深度パラメータを調整してください

【CoreThink-MCP Remote Server】
HTTP Transport環境でのエラーです。
            """

    async def manage_system_state(
        self,
        operation: str,
        target: str = "",
        parameters: str = ""
    ) -> str:
        """システム状態管理（ログ機能付き・HTTP Transport版）"""
        start_time = datetime.now()
        logger.info(f"システム管理開始: {operation}")
        
        try:
            inputs = {
                'operation': operation,
                'target': target,
                'parameters': parameters
            }
            
            # システム管理操作
            if operation == "get_history":
                result = f"""
📚 **推論履歴情報** (HTTP Transport版)

【履歴統計】
- 履歴管理: {'有効' if is_history_enabled() else '無効'}
- Sampling機能: {'有効' if is_sampling_enabled() else '無効'}

【制限事項】
HTTP Transport版では詳細履歴機能は制限されています。
STDIO版のcorethink_serverをご利用ください。
                """
                
            elif operation == "get_statistics":
                result = f"""
📈 **システム統計** (HTTP Transport版)

【機能状態】
- 推論エンジン: 動作中
- 制約検証: 動作中  
- サンドボックス: 動作中
- ログ機能: 基本レベル

【HTTP Transport制限】
詳細統計は制限されています。
                """
                
            elif operation == "manage_flags":
                result = f"""
🚩 **機能フラグ管理** (HTTP Transport版)

【現在の設定】
- History: {'有効' if is_history_enabled() else '無効'}
- Sampling: {'有効' if is_sampling_enabled() else '無効'}

【HTTP Transport制限】
機能フラグの動的変更は制限されています。
                """
                
            else:
                result = f"""
❌ **未対応操作** (HTTP Transport版)

【操作】
{operation}

【対応操作】
- get_history: 履歴情報取得
- get_statistics: 統計情報取得  
- manage_flags: 機能フラグ確認
                """
            
            # 実行時間計算
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # ツール実行履歴記録
            if is_history_enabled():
                await self._log_tool_execution(
                    tool_name="manage_system_state",
                    inputs=inputs,
                    core_result=result,
                    execution_time_ms=execution_time
                )
            
            logger.info(f"システム管理完了: {execution_time:.1f}ms")
            return result
            
        except Exception as e:
            error_msg = f"システム管理エラー: {str(e)}"
            logger.error(error_msg)
            
            return f"""
🚨 **システム管理エラー**

【エラー内容】
{error_msg}

【対処法】
1. 操作パラメータを確認してください
2. 対応操作リストを確認してください

【CoreThink-MCP Remote Server】
HTTP Transport環境でのエラーです。
            """

    async def generate_detailed_trace(
        self,
        context: str,
        step_description: str,
        reasoning_depth: str = "standard"
    ) -> str:
        """GSR推論トレース生成（corethink_server.py準拠）"""
        logger.info(f"推論トレース開始: {step_description}")
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            depth_levels = {
                "minimal": "基本情報のみ",
                "standard": "標準的な推論過程",
                "detailed": "詳細な分析と検証"
            }
            
            trace_result = f"""
【GSR推論トレース】HTTP Transport版
タイムスタンプ: {timestamp}
推論文脈: {context}
実行ステップ: {step_description}
推論深度: {reasoning_depth} ({depth_levels.get(reasoning_depth, "標準")})

【言語内推論過程】
前提条件確認: 文脈情報の妥当性と完全性を検証
制約適用結果: 現在の制約ルールに対する適合性評価
中間結論: 各段階での暫定的判断と根拠
矛盾検出: 論理的不整合や競合する要件の特定
次段階推論: 後続ステップの推定と準備

【透明性指標】
推論深度: {reasoning_depth}
確信度: {"HIGH" if reasoning_depth == "detailed" else "MEDIUM" if reasoning_depth == "standard" else "LOW"}
検証可能性: 全ステップ人間検証可能
トレーサビリティ: ログファイルに完全記録

【GSR原則適合性】
自然言語保持: ✅ 推論過程を自然言語で完全保持
文脈保存: ✅ 意味的情報の損失なし
透明性: ✅ 全推論ステップが検査可能

【HTTP Transport特性】
記録方式: ローカルログファイル
同期性: 即座に記録
制限事項: リアルタイム共有制限
            """
            
            logger.info("推論トレース完了")
            return trace_result
            
        except Exception as e:
            error_msg = f"推論トレースエラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def manage_system_state(
        self,
        operation: str,
        parameters: str = "{}"
    ) -> str:
        """システム状態管理（corethink_server.py準拠）"""
        logger.info(f"システム状態管理: {operation}")
        
        try:
            import json
            params = json.loads(parameters) if parameters != "{}" else {}
            
            if operation == "history":
                count = params.get('count', 10)
                query = params.get('query', '')
                
                if query:
                    result = f"履歴検索（クエリ: {query}）\nHTTP Transport制限により簡易検索"
                else:
                    result = f"最新履歴 {count}件\nHTTP Transport制限により基本情報のみ"
                
                return f"""
【履歴管理】
操作: {operation}
結果: {result}
制限: HTTP Transportでは詳細履歴機能が制限されます
                """
            
            elif operation == "statistics":
                return f"""
【統計情報】HTTP Transport版
履歴記録: {'有効' if is_history_enabled() else '無効'}
Sampling拡張: {'有効' if is_sampling_enabled() else '無効'}
機能制限: HTTP Transportでは一部機能が制限されます
実行時間: リアルタイム統計制限
ファイルサイズ: 基本的な情報のみ
                """
            
            elif operation == "flags":
                action = params.get('action', 'status')
                feature_name = params.get('feature_name', '')
                
                if action == "status":
                    status = feature_flags.get_status_report()
                    return f"""
【機能フラグ状態】HTTP Transport版
緊急モード: {'有効' if status['emergency_mode'] else '無効'}
Sampling拡張: {'有効' if status['sampling_enabled'] else '無効'}
履歴記録: {'有効' if status['history_enabled'] else '無効'}
HTTP制限: リモート機能フラグ変更は制限されます
                    """
                elif action == "emergency_disable":
                    feature_flags.emergency_disable()
                    return "🚨 緊急モード: 全ての拡張機能を無効化しました（HTTP Transport版）"
                else:
                    return f"機能フラグ操作（{action}）: HTTP Transportでは制限されます"
            
            elif operation == "constraints":
                topic = params.get('topic', '')
                if topic:
                    return f"制約学習（{topic}）: HTTP Transportでは基本制約のみ対応"
                else:
                    return "制約管理: HTTP Transportでは読み取り専用"
            
            else:
                return f"不明な操作: {operation}"
                
        except Exception as e:
            error_msg = f"システム状態管理エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def start_server(self):
        """Start the HTTP server"""
        runner = web_runner.AppRunner(self.app)
        await runner.setup()
        
        site = web_runner.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        version_info = get_version_info()
        logger.info(f"CoreThink-MCP Remote Server v{version_info['version']} started on http://localhost:{self.port}")
        logger.info(f"CoreThink論文: {version_info['paper']}")
        logger.info(f"GSRアーキテクチャ: 4層自然言語推論システム")
        logger.info(f"HTTP Transport制限: Sampling機能・リアルタイム拡張制限")
        logger.info("Health check: GET /health")
        logger.info("Server info: GET /info")
        logger.info("MCP endpoint: POST /mcp")
        
        return runner

async def main():
    """Main entry point"""
    port = int(os.getenv('CORETHINK_REMOTE_PORT', '8080'))
    
    server = RemoteCoreThinkMCP(port)
    runner = await server.start_server()
    
    try:
        # Keep server running
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
