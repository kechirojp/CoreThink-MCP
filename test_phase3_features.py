"""
Phase3 軽量拡張機能のテストスクリプト

新しく実装されたSampling拡張と履歴管理機能をテストします
"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.corethink_mcp.feature_flags import feature_flags, is_sampling_enabled, is_history_enabled
from src.corethink_mcp.history_manager import log_tool_execution, get_history_stats, get_recent_reasoning

async def test_feature_flags():
    """機能フラグシステムのテスト"""
    print("🧪 機能フラグシステムテスト")
    print("-" * 50)
    
    # 初期状態確認
    print(f"Sampling拡張: {'有効' if is_sampling_enabled() else '無効'}")
    print(f"履歴記録: {'有効' if is_history_enabled() else '無効'}")
    
    # 状態レポート
    status = feature_flags.get_status_report()
    print(f"緊急モード: {'有効' if status['emergency_mode'] else '無効'}")
    print(f"設定ファイル: {status['config_file']}")
    
    # 機能有効化テスト
    print("\n📝 機能有効化テスト:")
    feature_flags.set_flag('ENABLE_SAMPLING_ENHANCEMENT', True)
    feature_flags.set_flag('ENABLE_HISTORY_LOGGING', True)
    print(f"Sampling拡張: {'有効' if is_sampling_enabled() else '無効'}")
    print(f"履歴記録: {'有効' if is_history_enabled() else '無効'}")
    
    print("✅ 機能フラグテスト完了\n")

async def test_history_manager():
    """履歴管理システムのテスト"""
    print("📚 履歴管理システムテスト")
    print("-" * 50)
    
    # 履歴記録テスト
    test_inputs = {
        'user_intent': 'テストファイルの作成',
        'current_state': 'プロジェクト初期状態',
        'proposed_action': 'test_file.py を作成'
    }
    
    test_result = """
【CoreThink推論結果】
意図: テストファイルの作成
分析: 安全な操作として判定
判定: PROCEED
    """.strip()
    
    sampling_result = """
【補助分析】
- ファイル名に適切な拡張子が使用されている
- 既存ファイルとの競合なし
- テスト目的として適切
    """.strip()
    
    # 履歴記録実行
    log_tool_execution(
        tool_name="reason_about_change",
        inputs=test_inputs,
        result=test_result,
        sampling_result=sampling_result,
        execution_time_ms=125.5
    )
    
    print("📝 テスト履歴を記録しました")
    
    # 統計情報確認
    stats = get_history_stats()
    print(f"総エントリ数: {stats.get('total_entries', 0)}")
    print(f"ファイルサイズ: {stats.get('file_size_mb', 0)} MB")
    print(f"ファイルパス: {stats.get('file_path', 'Unknown')}")
    
    # 最近の履歴取得
    recent = get_recent_reasoning(count=3)
    print(f"最近の履歴エントリ: {len(recent)}件")
    
    print("✅ 履歴管理テスト完了\n")

async def test_sampling_simulation():
    """Sampling機能のシミュレーションテスト"""
    print("🤖 Sampling機能シミュレーションテスト")
    print("-" * 50)
    
    # MockContextクラス（実際のFastMCP contextをシミュレート）
    class MockSamplingContext:
        async def sample(self, query: str) -> str:
            """サンプルSampling応答を返す"""
            return f"""
【模擬Sampling応答】
クエリ: {query[:50]}...

追加考慮点:
1. エラーハンドリングの追加検討
2. パフォーマンス最適化の余地
3. ユーザーフィードバックの収集

代替案:
- より保守的なアプローチも検討可能
- 段階的実装による リスク軽減

注意点:
- 既存システムへの影響を監視
- ロールバック準備を万全に
            """.strip()
    
    # Sampling拡張のシミュレーション
    if is_sampling_enabled():
        mock_ctx = MockSamplingContext()
        
        core_result = "【判定】PROCEED_WITH_CAUTION\n【理由】詳細検証が必要"
        
        # 実際のサーバーコードからインポートして使用するのは難しいため、
        # ここでは機能の動作確認のみ実行
        sampling_query = f"CoreThink推論結果への追加考慮: {core_result}"
        sampling_response = await mock_ctx.sample(sampling_query)
        
        print("📤 Samplingクエリ送信:")
        print(sampling_query[:100] + "...")
        print("\n📥 Sampling応答受信:")
        print(sampling_response[:200] + "...")
        
        print("\n✅ Sampling拡張シミュレーション完了")
    else:
        print("⚠️  Sampling拡張が無効のため、シミュレーションをスキップします")
    
    print()

async def test_error_handling():
    """エラーハンドリングのテスト"""
    print("🛡️ エラーハンドリングテスト")
    print("-" * 50)
    
    # 緊急無効化テスト
    print("緊急無効化をテスト...")
    feature_flags.emergency_disable()
    
    print(f"緊急モード後 - Sampling: {'有効' if is_sampling_enabled() else '無効'}")
    print(f"緊急モード後 - 履歴: {'有効' if is_history_enabled() else '無効'}")
    
    # 復旧テスト
    print("\n緊急モード解除をテスト...")
    feature_flags.emergency_restore()
    feature_flags.set_flag('ENABLE_SAMPLING_ENHANCEMENT', True)
    feature_flags.set_flag('ENABLE_HISTORY_LOGGING', True)
    
    print(f"復旧後 - Sampling: {'有効' if is_sampling_enabled() else '無効'}")
    print(f"復旧後 - 履歴: {'有効' if is_history_enabled() else '無効'}")
    
    print("✅ エラーハンドリングテスト完了\n")

async def main():
    """メインテスト実行"""
    print("🚀 Phase3 軽量拡張機能テスト開始")
    print("=" * 60)
    
    try:
        await test_feature_flags()
        await test_history_manager()
        await test_sampling_simulation()
        await test_error_handling()
        
        print("🎉 全てのテストが完了しました！")
        print("\n📋 次のステップ:")
        print("1. MCPサーバーを起動してVS CodeやClaude Desktopで機能を確認")
        print("2. 実際のSampling機能を有効化して動作テスト")
        print("3. 履歴ファイル（logs/reasoning_history.md）の確認")
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
