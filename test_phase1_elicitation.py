"""
Phase 1 Elicitation実装テスト
FastMCP標準elicitationパターンの動作確認
"""

import asyncio
import logging
from fastmcp import Client
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_elicitation_integration():
    """Elicitation統合の動作テスト"""
    
    print("🚀 Phase 1: FastMCP Elicitation統合テスト開始")
    
    # CoreThink-MCP サーバースクリプトのパス
    server_script = Path(__file__).parent / "src" / "corethink_mcp" / "server" / "corethink_server.py"
    
    if not server_script.exists():
        print(f"❌ サーバースクリプトが見つかりません: {server_script}")
        return
    
    try:
        # FastMCPクライアントでサーバーに接続
        async with Client(str(server_script)) as client:
            print("✅ FastMCPクライアントでサーバーに接続成功")
            
            # ツール一覧確認
            tools = await client.list_tools()
            print(f"📋 利用可能なツール: {len(tools)}個")
            for tool in tools:
                print(f"  - {tool.name}")
            
            # Test Case 1: 不完全なパラメータでElicitation発生を期待
            print("\n🧪 Test Case 1: Elicitation統合テスト")
            print("不完全なパラメータで refine_understanding を実行")
            
            # 意図的に context_clues と domain_hints を空にしてElicitationを誘発
            test_params = {
                "ambiguous_request": "システムのパフォーマンスを向上させたい",
                # context_clues と domain_hints を意図的に省略してElicitationをテスト
            }
            
            try:
                result = await client.call_tool("refine_understanding", test_params)
                print("📊 実行結果:")
                print("=" * 80)
                for content in result.content:
                    print(content.text)
                print("=" * 80)
                print("✅ Test Case 1 完了")
                
            except Exception as e:
                print(f"❌ Test Case 1 エラー: {str(e)}")
                print("詳細:", e.__class__.__name__)
                
            # Test Case 2: 完全なパラメータで通常実行をテスト
            print("\n🧪 Test Case 2: 完全パラメータテスト")
            
            complete_params = {
                "ambiguous_request": "データベースの最適化をしたい",
                "context_clues": "レスポンス時間が遅い、ピーク時にタイムアウト発生",
                "domain_hints": "技術・データベース管理"
            }
            
            try:
                result = await client.call_tool("refine_understanding", complete_params)
                print("📊 実行結果:")
                print("=" * 80)
                for content in result.content:
                    print(content.text)
                print("=" * 80)
                print("✅ Test Case 2 完了")
                
            except Exception as e:
                print(f"❌ Test Case 2 エラー: {str(e)}")
                print("詳細:", e.__class__.__name__)
                
    except Exception as e:
        print(f"❌ クライアント接続エラー: {str(e)}")
        print("詳細:", e.__class__.__name__)

if __name__ == "__main__":
    asyncio.run(test_elicitation_integration())
