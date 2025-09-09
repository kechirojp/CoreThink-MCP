#!/usr/bin/env python3
"""
CoreThink-MCP 自動同期スクリプト実行用ランナー
"""

import sys
from pathlib import Path
from sync_generator import main

def run_sync():
    """同期スクリプトを実行"""
    print("🔄 CoreThink-MCP 自動同期を開始します...")
    
    result = main()
    
    if result == 0:
        print("\n✅ 自動同期が正常に完了しました！")
        print("🔧 次のステップ:")
        print("  1. cd nodejs && npm run build でコンパイル")
        print("  2. npm start でNode.jsサーバー実行")
        print("  3. VS Codeで両サーバーのツール数を確認")
    else:
        print("\n❌ 自動同期でエラーが発生しました")
        print("🔍 ログを確認して問題を修正してください")
    
    return result

if __name__ == "__main__":
    sys.exit(run_sync())
