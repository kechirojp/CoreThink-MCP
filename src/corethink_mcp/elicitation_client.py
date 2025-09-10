#!/usr/bin/env python3
"""
CoreThink-MCP Elicitation クライアント実装
ユーザーとのインタラクティブな対話を通じてツール実行を支援
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreThinkElicitationClient:
    """CoreThink-MCP Elicitation クライアント"""
    
    def __init__(self, server_path: str = None):
        self.server_path = server_path or "i:\\CoreThink-MCP\\src\\corethink_mcp\\elicitation_server.py"
        self.client = None
    
    async def elicitation_handler(
        self, 
        message: str, 
        response_type: type, 
        params: Any, 
        context: Any
    ) -> Any:
        """
        FastMCP Elicitation ハンドラー
        ユーザーからの入力を収集して構造化されたレスポンスを生成
        """
        logger.info(f"Elicitation 要求: {message}")
        
        try:
            # ユーザーにメッセージを表示して入力を収集
            print(f"\n🤖 CoreThink-MCP: {message}")
            user_input = input("👤 あなた: ")
            
            # 空入力の場合は decline
            if not user_input.strip():
                logger.info("ユーザーが入力を拒否")
                return ElicitResult(action="decline")
            
            # "cancel" や "キャンセル" の場合は cancel
            if user_input.lower() in ["cancel", "キャンセル", "中止", "やめる"]:
                logger.info("ユーザーが操作をキャンセル")
                return ElicitResult(action="cancel")
            
            # response_type が None の場合（空オブジェクト要求）
            if response_type is None:
                logger.info("空レスポンス要求 - accept で応答")
                return ElicitResult(action="accept", content=None)
            
            # FastMCP が提供する dataclass タイプを使用してレスポンス作成
            if hasattr(response_type, '__annotations__'):
                # dataclass の場合
                if 'value' in response_type.__annotations__:
                    response_data = response_type(value=user_input)
                else:
                    # フィールド名を推測
                    fields = list(response_type.__annotations__.keys())
                    if fields:
                        response_data = response_type(**{fields[0]: user_input})
                    else:
                        response_data = response_type()
            else:
                # 単純な値の場合
                response_data = user_input
            
            logger.info(f"レスポンス生成: {response_data}")
            return response_data  # 暗黙的に accept
            
        except Exception as e:
            logger.error(f"Elicitation ハンドラーエラー: {e}")
            return ElicitResult(action="decline")
    
    async def run_interactive_analysis(self, initial_request: str = "分析お願い"):
        """インタラクティブ分析の実行"""
        print(f"\n🚀 CoreThink-MCP インタラクティブ分析を開始します")
        print(f"📝 初期要求: {initial_request}")
        
        try:
            # Elicitation ハンドラー付きクライアントを作成
            self.client = Client(
                self.server_path,
                elicitation_handler=self.elicitation_handler
            )
            
            async with self.client:
                print("✅ サーバーに接続しました")
                
                # 利用可能なツールを確認
                tools = await self.client.list_tools()
                print(f"📋 利用可能なツール: {len(tools)} 個")
                
                # インタラクティブ分析を実行
                print("\n🔍 インタラクティブ分析を開始...")
                result = await self.client.call_tool(
                    "interactive_corethink",
                    {"initial_request": initial_request}
                )
                
                print(f"\n📊 分析結果:")
                print("=" * 60)
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                print("=" * 60)
                
        except Exception as e:
            logger.error(f"インタラクティブ分析エラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
    
    async def run_auto_analysis(self, request: str = "システムのパフォーマンスを向上させて"):
        """自動分析の実行"""
        print(f"\n🚀 CoreThink-MCP 自動分析を開始します")
        print(f"📝 要求: {request}")
        
        try:
            self.client = Client(self.server_path)
            
            async with self.client:
                print("✅ サーバーに接続しました")
                
                # 自動分析を実行
                print("\n⚡ 自動分析を実行中...")
                result = await self.client.call_tool(
                    "corethink_auto_analysis",
                    {
                        "request": request,
                        "auto_mode": True
                    }
                )
                
                print(f"\n📊 自動分析結果:")
                print("=" * 60)
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                print("=" * 60)
                
        except Exception as e:
            logger.error(f"自動分析エラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
    
    async def run_smart_dispatch(self, user_input: str):
        """スマートディスパッチの実行"""
        print(f"\n🧠 CoreThink-MCP スマートディスパッチ")
        print(f"💬 入力: {user_input}")
        
        try:
            self.client = Client(
                self.server_path,
                elicitation_handler=self.elicitation_handler
            )
            
            async with self.client:
                print("✅ サーバーに接続しました")
                
                # スマートディスパッチを実行
                print("\n🎯 適切なツールを選択中...")
                result = await self.client.call_tool(
                    "smart_tool_dispatcher",
                    {"user_input": user_input}
                )
                
                print(f"\n📊 ディスパッチ結果:")
                print("=" * 60)
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                print("=" * 60)
                
        except Exception as e:
            logger.error(f"スマートディスパッチエラー: {e}")
            print(f"❌ エラーが発生しました: {e}")
    
    async def demo_all_features(self):
        """全機能のデモンストレーション"""
        print("🎭 CoreThink-MCP Elicitation 機能デモ")
        print("=" * 50)
        
        # 1. 自動分析
        await self.run_auto_analysis("システムのパフォーマンスを向上させて")
        
        input("\n⏸️  次のデモに進むには Enter を押してください...")
        
        # 2. スマートディスパッチ
        await self.run_smart_dispatch("曖昧な要求を明確化したい")
        
        input("\n⏸️  次のデモに進むには Enter を押してください...")
        
        # 3. インタラクティブ分析
        await self.run_interactive_analysis("データベースの設計を改善したい")
        
        print("\n🎉 全機能のデモが完了しました！")

async def main():
    """メイン実行関数"""
    client = CoreThinkElicitationClient()
    
    print("🤖 CoreThink-MCP Elicitation クライアント")
    print("=" * 50)
    print("1. 自動分析デモ")
    print("2. スマートディスパッチデモ") 
    print("3. インタラクティブ分析デモ")
    print("4. 全機能デモ")
    print("5. カスタム分析")
    
    choice = input("\n選択してください (1-5): ")
    
    if choice == "1":
        request = input("分析要求を入力してください (Enter でデフォルト): ").strip()
        if not request:
            request = "システムのパフォーマンスを向上させて"
        await client.run_auto_analysis(request)
    
    elif choice == "2":
        user_input = input("自然言語で要求を入力してください: ").strip()
        if user_input:
            await client.run_smart_dispatch(user_input)
        else:
            print("❌ 入力が必要です")
    
    elif choice == "3":
        request = input("初期要求を入力してください (Enter でデフォルト): ").strip()
        if not request:
            request = "分析お願い"
        await client.run_interactive_analysis(request)
    
    elif choice == "4":
        await client.demo_all_features()
    
    elif choice == "5":
        print("🔧 カスタム分析モード")
        request = input("要求: ")
        mode = input("モード (auto/interactive): ").strip().lower()
        
        if mode == "interactive":
            await client.run_interactive_analysis(request)
        else:
            await client.run_auto_analysis(request)
    
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    asyncio.run(main())
