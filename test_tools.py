#!/usr/bin/env python3
"""
CoreThink-MCP の個別ツールテスト
"""
import asyncio
import json
import subprocess
import sys
import time

async def test_specific_tool(tool_name: str, params: dict):
    """特定のツールをテストします"""
    
    # サーバープロセスを起動
    process = subprocess.Popen(
        [sys.executable, "src/corethink_mcp/server/corethink_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=".",
        encoding="utf-8"
    )
    
    try:
        # 初期化
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # レスポンス待機
        init_response = process.stdout.readline()
        print(f"📥 初期化応答: {init_response.strip()}")
        
        # 初期化完了通知
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # ツール実行
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        print(f"\n🛠  ツール '{tool_name}' を呼び出し中...")
        print(f"📤 パラメータ: {json.dumps(params, ensure_ascii=False, indent=2)}")
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # 結果を取得
        tool_response = process.stdout.readline()
        if tool_response:
            try:
                response_data = json.loads(tool_response.strip())
                print(f"\n📥 ツール実行結果:")
                print(json.dumps(response_data, ensure_ascii=False, indent=2))
            except json.JSONDecodeError as e:
                print(f"❌ JSON デコードエラー: {e}")
                print(f"Raw response: {tool_response}")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        
    finally:
        process.terminate()
        process.wait()

async def main():
    """メインテスト関数"""
    print("🧪 CoreThink-MCP ツール個別テスト\n")
    
    # 1. reason_about_change のテスト
    print("=" * 50)
    await test_specific_tool("reason_about_change", {
        "user_intent": "calc.pyのゼロ除算バグを修正したい",
        "current_state": "ZeroDivisionError が発生している", 
        "proposed_action": "例外処理を追加する"
    })
    
    # 少し待機
    time.sleep(2)
    
    # 2. validate_against_constraints のテスト
    print("=" * 50)
    await test_specific_tool("validate_against_constraints", {
        "proposed_change": "try-except文を追加",
        "reasoning_context": "ゼロ除算エラーの処理"
    })
    
    # 少し待機
    time.sleep(2)
    
    # 3. execute_with_safeguards のテスト
    print("=" * 50)
    await test_specific_tool("execute_with_safeguards", {
        "action_description": "ゼロ除算処理の追加",
        "dry_run": True
    })

if __name__ == "__main__":
    asyncio.run(main())
