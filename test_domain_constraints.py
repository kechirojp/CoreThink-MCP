#!/usr/bin/env python3
"""分野特化制約システムのテスト"""

import asyncio
from src.corethink_mcp.server.corethink_server import reason_about_change

async def test_domain_constraints():
    """各分野での制約適用をテスト"""
    
    print("🧪 分野特化制約システム テスト\n")
    
    # テストケース
    test_cases = [
        {
            "name": "医療分野",
            "user_intent": "患者の血圧データを管理する新機能を追加したい",
            "current_state": "現在は基本的なデータ収集のみ",
            "proposed_action": "血圧アラート機能を追加"
        },
        {
            "name": "法律分野", 
            "user_intent": "法的文書の分類システムを改善したい",
            "current_state": "基本的な分類が可能",
            "proposed_action": "AI判断による自動分類を追加"
        },
        {
            "name": "エンジニアリング分野",
            "user_intent": "データベースのパフォーマンスを改善したい",
            "current_state": "クエリが遅い",
            "proposed_action": "インデックスを追加"
        },
        {
            "name": "AI・機械学習分野",
            "user_intent": "機械学習モデルの精度を向上させたい",
            "current_state": "現在の精度は80%",
            "proposed_action": "ハイパーパラメータを調整"
        },
        {
            "name": "クラウド・DevOps分野",
            "user_intent": "Kubernetesクラスターを最適化したい", 
            "current_state": "リソース使用率が高い",
            "proposed_action": "オートスケーリングを設定"
        },
        {
            "name": "安全重要分野",
            "user_intent": "自動運転車の制御システムを更新したい",
            "current_state": "現在のシステムが動作中",
            "proposed_action": "新しい回避アルゴリズムを追加"
        }
    ]
    
    # 各テストケースを実行
    for i, case in enumerate(test_cases, 1):
        print(f"==== テスト {i}: {case['name']} ====")
        try:
            result = await reason_about_change(
                user_intent=case["user_intent"],
                current_state=case["current_state"], 
                proposed_action=case["proposed_action"]
            )
            
            # 分野特化制約が適用されているかチェック
            if "医療" in case["name"] and "HIPAA" in result:
                print("✅ 医療分野制約が適用されました")
            elif "法律" in case["name"] and "法的責任" in result:
                print("✅ 法律分野制約が適用されました")
            elif "エンジニアリング" in case["name"] and ("パフォーマンス" in result or "テスト" in result):
                print("✅ エンジニアリング分野制約が適用されました")
            elif "AI・機械学習" in case["name"] and ("バイアス" in result or "AI" in result):
                print("✅ AI・機械学習分野制約が適用されました")
            elif "クラウド" in case["name"] and ("セキュリティ" in result or "クラウド" in result):
                print("✅ クラウド・DevOps分野制約が適用されました")
            elif "安全重要" in case["name"] and ("安全" in result or "フェイルセーフ" in result):
                print("✅ 安全重要分野制約が適用されました")
            else:
                print("⚠️ 基本制約のみ適用（分野特化制約検出されず）")
            
            print(f"結果 (最初の200文字): {result[:200]}...")
            print()
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            print()
    
    print("🎯 全テスト完了")

if __name__ == "__main__":
    asyncio.run(test_domain_constraints())
