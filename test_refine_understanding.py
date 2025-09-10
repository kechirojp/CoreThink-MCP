#!/usr/bin/env python3
"""
FastMCP Client を使って refine_understanding ツールをテストするスクリプト
"""
import asyncio
from fastmcp import Client

async def test_refine_understanding():
    """refine_understanding ツールをテストする"""
    
    # STDIO トランスポートで my-mcp-server-CoreThink-MPC に接続
    # FastMCP Client は実行可能ファイルのパスを期待する
    server_script = "i:\\CoreThink-MCP\\src\\corethink_mcp\\server\\corethink_server.py"
    
    print("🚀 CoreThink-MCP サーバーに接続中...")
    
    async with Client(server_script) as client:
        print("✅ サーバーに接続完了")
        
        # 利用可能なツール一覧を確認
        tools = await client.list_tools()
        print(f"\n📋 利用可能なツール数: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # refine_understanding ツールを実行
        print("\n🔍 refine_understanding ツールを実行中...")
        
        params = {
            "ambiguous_request": "システムのパフォーマンスを向上させて",
            "context_clues": "論文Section 5.1の「Native Language Parsing & Semantic Preservation」に基づく曖昧性解消。パフォーマンス（レスポンス時間？スループット？）、システム範囲（API？データベース？フロントエンド？）、向上目標値（現在状況？改善幅？）、制約条件（予算？スケジュール？既存機能影響？）を明確化し、実行可能な具体的タスクに変換する。",
            "domain_hints": "システムパフォーマンス最適化"
        }
        
        result = await client.call_tool("refine_understanding", params)
        
        print("\n📊 実行結果:")
        print("=" * 80)
        for content in result.content:
            print(content.text)
        print("=" * 80)
        
        print("\n✅ テスト完了")

if __name__ == "__main__":
    asyncio.run(test_refine_understanding())
