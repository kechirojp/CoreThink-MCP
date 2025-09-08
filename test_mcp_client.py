#!/usr/bin/env python3
"""
CoreThink-MCP サーバーのテスト用クライアント
"""
import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """MCPサーバーをテストします"""
    
    # サーバープロセスを起動
    process = subprocess.Popen(
        [sys.executable, "src/corethink_mcp/server/corethink_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="."
    )
    
    try:
        # 初期化リクエスト
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 初期化リクエストを送信中...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # レスポンスを読み取り
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print("📥 サーバーからの応答:")
                print(json.dumps(response, indent=2, ensure_ascii=False))
                
                # 初期化完了通知を送信
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                print("\n📤 初期化完了通知を送信中...")
                process.stdin.write(json.dumps(initialized_notification) + "\n")
                process.stdin.flush()
                
                # ツール一覧を取得
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                print("\n📤 ツール一覧リクエストを送信中...")
                process.stdin.write(json.dumps(tools_request) + "\n")
                process.stdin.flush()
                
                tools_response_line = process.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.strip())
                    print("📥 利用可能なツール:")
                    print(json.dumps(tools_response, indent=2, ensure_ascii=False))
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSONデコードエラー: {e}")
                print(f"Raw response: {response_line}")
                
    except Exception as e:
        print(f"❌ テスト中にエラーが発生: {e}")
        
    finally:
        process.terminate()
        process.wait()
        
        # stderrの内容を確認
        stderr_output = process.stderr.read()
        if stderr_output:
            print("\n📝 サーバーログ (stderr):")
            print(stderr_output)

if __name__ == "__main__":
    print("🧪 CoreThink-MCP サーバーテストを開始...")
    asyncio.run(test_mcp_server())
