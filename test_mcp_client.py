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
        encoding="utf-8",
        errors="replace",
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
                    
                    # refine_understanding ツールを呼び出して曖昧性解消を実行
                    refine_call = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "refine_understanding",
                            "arguments": {
                                "ambiguous_request": "システムのパフォーマンスを向上させて",
                                "context_clues": (
                                    "対象: MCPサーバー(my-mcp-server-CoreThink-MPC)のツール実行経路。"
                                    "評価指標候補: レスポンスp95, スループットRPS, エラー率, CPU/メモリ。"
                                    "範囲: tools/call〜処理〜応答の往復。制約: 既存IF不変・自然言語出力維持。"
                                ),
                                "domain_hints": "ソフトウェア性能最適化, MCP, API"
                            }
                        }
                    }
                    
                    print("\n📤 refine_understanding を呼び出し中...")
                    process.stdin.write(json.dumps(refine_call) + "\n")
                    process.stdin.flush()
                    
                    # 返答の一行を取得（証跡目的で十分）
                    refine_response_line = process.stdout.readline()
                    if refine_response_line:
                        try:
                            refine_response = json.loads(refine_response_line.strip())
                            print("📥 refine_understanding 応答(抜粋):")
                            # 応答全体は長い可能性があるため先頭部分のみ表示
                            print(json.dumps(refine_response, indent=2, ensure_ascii=False)[:1000] + "...")
                        except json.JSONDecodeError:
                            print("ℹ️ 非JSONレスポンス(先頭行):", refine_response_line[:200])
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSONデコードエラー: {e}")
                print(f"Raw response: {response_line}")
                
    except Exception as e:
        print(f"❌ テスト中にエラーが発生: {e}")
        
    finally:
        process.terminate()
        process.wait()
        
        # stderrの内容を確認
        try:
            stderr_output = process.stderr.read()
            if stderr_output:
                print("\n📝 サーバーログ (stderr):")
                print(stderr_output)
        except Exception as e:
            print(f"(stderr取得スキップ: {e})")

if __name__ == "__main__":
    print("🧪 CoreThink-MCP サーバーテストを開始...")
    asyncio.run(test_mcp_server())
