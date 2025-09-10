"""
CoreThink-MCP Elicitation統合サンプル
FastMCP Client を使って Elicitation 機能をテストするスンプル
"""

import asyncio
import json
from fastmcp import Client
from src.corethink_mcp.elicitation import elicitation_handler

async def test_elicitation_integration():
    """Elicitation機能の統合テスト"""
    
    print("🚀 CoreThink-MCP Elicitation 統合テスト開始")
    
    # CoreThink-MCP サーバーに接続（Elicitationハンドラー付き）
    server_script = "i:\\CoreThink-MCP\\src\\corethink_mcp\\server\\corethink_server.py"
    
    async with Client(server_script, elicitation_handler=elicitation_handler) as client:
        print("✅ Elicitation対応クライアントでサーバーに接続")
        
        # ツール一覧確認
        tools = await client.list_tools()
        print(f"📋 利用可能なツール: {len(tools)}個")
        
        # Elicitationが発生しそうなケースをテスト
        print("\n🧪 テストケース1: 不完全なパラメータでrefine_understanding実行")
        
        # 意図的に不完全なパラメータで実行
        incomplete_params = {
            "ambiguous_request": "システムのパフォーマンスを向上させて"
            # context_clues と domain_hints を意図的に省略
        }
        
        try:
            result = await client.call_tool("refine_understanding", incomplete_params)
            print("📊 実行結果:")
            print("=" * 80)
            for content in result.content:
                print(content.text)
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ エラー: {str(e)}")
        
        print("\n🧪 テストケース2: 段階的なパラメータ収集")
        
        # より複雑なケース（複数の不足パラメータ）
        minimal_params = {
            "user_intent": "バグ修正したい"
            # current_state と proposed_action を省略
        }
        
        try:
            result = await client.call_tool("reason_about_change", minimal_params)
            print("📊 段階的収集結果:")
            print("=" * 80)
            for content in result.content:
                print(content.text)
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ エラー: {str(e)}")

async def test_elicitation_workflow():
    """Elicitationワークフローのテスト"""
    
    print("\n🔄 Elicitationワークフロー詳細テスト")
    
    # テスト用の模擬シナリオ
    scenarios = [
        {
            "name": "曖昧性解消支援",
            "tool": "refine_understanding",
            "initial_params": {
                "ambiguous_request": "性能改善して"
            },
            "expected_elicitations": ["context_clues", "domain_hints"]
        },
        {
            "name": "制約検証支援", 
            "tool": "validate_against_constraints",
            "initial_params": {
                "proposed_change": "コード変更"
            },
            "expected_elicitations": ["reasoning_context"]
        }
    ]
    
    server_script = "i:\\CoreThink-MCP\\src\\corethink_mcp\\server\\corethink_server.py"
    
    async with Client(server_script, elicitation_handler=elicitation_handler) as client:
        
        for scenario in scenarios:
            print(f"\n📋 シナリオ: {scenario['name']}")
            print(f"🎯 ツール: {scenario['tool']}")
            print(f"📥 初期パラメータ: {scenario['initial_params']}")
            
            try:
                result = await client.call_tool(
                    scenario['tool'], 
                    scenario['initial_params']
                )
                
                print("✅ 実行成功")
                print(f"📤 結果サマリ: {len(result.content)}個のコンテンツ")
                
                # 最初の200文字だけ表示
                if result.content:
                    preview = result.content[0].text[:200]
                    print(f"🔍 プレビュー: {preview}...")
                
            except Exception as e:
                print(f"❌ シナリオ失敗: {str(e)}")

async def main():
    """メインテスト実行"""
    
    print("🧠 CoreThink-MCP Elicitation機能 総合テスト")
    print("=" * 80)
    
    # 基本的な統合テスト
    await test_elicitation_integration()
    
    print("\n" + "=" * 80)
    
    # ワークフローテスト
    await test_elicitation_workflow()
    
    print("\n✨ テスト完了")

if __name__ == "__main__":
    asyncio.run(main())
