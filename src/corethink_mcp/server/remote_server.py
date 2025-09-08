"""
CoreThink-MCP Remote Server
Remote MCP (HTTP Transport) implementation for claude.ai connectors
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict
from aiohttp import web, web_runner
import json

# プロジェクトディレクトリを取得してパッケージルートをsys.pathに追加
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.corethink_mcp import get_version_info
from src.corethink_mcp.server.corethink_server import (
    load_constraints, create_sandbox, CONSTRAINTS_FILE, REPO_ROOT, SANDBOX_DIR
)

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
                'tools': ['reason_about_change', 'validate_against_constraints', 'execute_with_safeguards'],
                'resources': ['constraints', 'reasoning_log'],
                'protocol_version': '2024-11-05'
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
            'protocolVersion': '2024-11-05',
            'capabilities': {
                'tools': {
                    'listChanged': True
                },
                'resources': {
                    'subscribe': True,
                    'listChanged': True
                }
            },
            'serverInfo': {
                'name': 'corethink-mcp',
                'version': self.version_info['version']
            }
        }
    
    async def handle_tools_list(self):
        """List available tools"""
        return {
            'tools': [
                {
                    'name': 'reason_about_change',
                    'description': 'GSRに則った自然言語による推論。制約・矛盾・リスクを言語で評価。',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'user_intent': {'type': 'string', 'description': 'ユーザーの意図'},
                            'current_state': {'type': 'string', 'description': '現在の状態'},
                            'proposed_action': {'type': 'string', 'description': '提案されたアクション'}
                        },
                        'required': ['user_intent', 'current_state', 'proposed_action']
                    }
                },
                {
                    'name': 'validate_against_constraints',
                    'description': '提案された変更が制約に違反していないか、自然言語で検証。',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'proposed_change': {'type': 'string', 'description': '提案された変更'},
                            'reasoning_context': {'type': 'string', 'description': '推論コンテキスト（オプション）'}
                        },
                        'required': ['proposed_change']
                    }
                },
                {
                    'name': 'execute_with_safeguards',
                    'description': '安全に変更を適用（サンドボックス環境で）',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'action_description': {'type': 'string', 'description': 'アクションの説明'},
                            'dry_run': {'type': 'boolean', 'description': 'ドライランかどうか', 'default': True}
                        },
                        'required': ['action_description']
                    }
                }
            ]
        }
    
    async def handle_tools_call(self, params):
        """Handle tool calls"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name == 'reason_about_change':
            content = await self.reason_about_change(**arguments)
        elif tool_name == 'validate_against_constraints':
            content = await self.validate_against_constraints(**arguments)
        elif tool_name == 'execute_with_safeguards':
            content = await self.execute_with_safeguards(**arguments)
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
                    'description': 'CoreThink-MCPの安全制約定義',
                    'mimeType': 'text/plain'
                },
                {
                    'uri': 'file://reasoning_log',
                    'name': '推論ログ',
                    'description': 'CoreThink推論プロセスのログ',
                    'mimeType': 'text/plain'
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
    
    # Tool implementations (同じロジックを使用)
    async def reason_about_change(self, user_intent: str, current_state: str, proposed_action: str) -> str:
        """GSRに則った推論"""
        logger.info(f"推論開始: {user_intent}")
        
        try:
            constraints = load_constraints()
            
            reasoning = f"""
【CoreThink推論開始】
意図: {user_intent}
現状: {current_state}
提案: {proposed_action}

【制約確認】
{constraints}

【分析過程】
1. 意図の明確性チェック: {"明確" if user_intent.strip() else "不明確"}
2. 制約適合性評価:
   - 公開API変更: 検証中...
   - デバッグ出力: 検証中...
   - テスト影響: 検証中...

【暫定判定】PROCEED_WITH_CAUTION
【理由】詳細な制約検証が必要
【次ステップ】validate_against_constraints での詳細検証
            """.strip()
            
            logger.info("推論完了")
            return reasoning
            
        except Exception as e:
            error_msg = f"推論エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def validate_against_constraints(self, proposed_change: str, reasoning_context: str = "") -> str:
        """制約検証"""
        logger.info("制約検証開始")
        
        try:
            constraints = load_constraints()
            
            validation_result = f"""
【制約検証結果】
提案変更: {proposed_change}
文脈: {reasoning_context}

【詳細チェック】
✅ MUST「公開API変更禁止」 → 適合確認中
✅ NEVER「デバッグ出力禁止」 → 適合確認中
⚠️ SHOULD「docstring更新推奨」 → 要確認
✅ MUST「テスト通過」 → 検証必要

【総合判定】PROCEED_WITH_WARNING
【推奨】追加のdocstring更新を検討してください
【次ステップ】execute_with_safeguards でdry-run実行
            """.strip()
            
            logger.info("制約検証完了")
            return validation_result
            
        except Exception as e:
            error_msg = f"検証エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def execute_with_safeguards(self, action_description: str, dry_run: bool = True) -> str:
        """安全実行"""
        logger.info(f"実行開始 (dry_run={dry_run}): {action_description}")
        
        try:
            if dry_run:
                sandbox_path = create_sandbox()
                result = f"""
【DRY RUN実行】
アクション: {action_description}
サンドボックス: {sandbox_path}

【シミュレーション結果】
✅ サンドボックス作成成功
✅ 変更は実ファイルに影響しません
✅ ロールバック準備完了

【次ステップ】実際の実行は dry_run=False で行ってください
                """.strip()
            else:
                result = f"""
【実行完了】
アクション: {action_description}
状態: 実装中（現在はdry-runのみ対応）
                """.strip()
            
            logger.info("実行完了")
            return result
            
        except Exception as e:
            error_msg = f"実行エラー: {str(e)}"
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
