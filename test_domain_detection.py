#!/usr/bin/env python3
"""分野検出ロジックのテスト"""

from src.corethink_mcp.server.corethink_server import _detect_domain, load_domain_constraints

def test_domain_detection():
    """分野検出機能のテスト"""
    
    print("🧪 分野検出テスト\n")
    
    test_cases = [
        {
            "text": "患者の血圧データを管理する新機能を追加したい",
            "expected": "medical"
        },
        {
            "text": "法的文書の分類システムを改善したい",
            "expected": "legal"
        },
        {
            "text": "データベースのパフォーマンスを改善したい",
            "expected": "engineering"
        },
        {
            "text": "機械学習モデルの精度を向上させたい",
            "expected": "ai_ml"
        },
        {
            "text": "Kubernetesクラスターを最適化したい",
            "expected": "cloud_devops"
        },
        {
            "text": "自動運転車の制御システムを更新したい",
            "expected": "safety_critical"
        },
        {
            "text": "計算機のメモリ使用量を確認したい",
            "expected": "general"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        detected = _detect_domain(case["text"])
        status = "✅" if detected == case["expected"] else "❌"
        print(f"{i}. テキスト: {case['text'][:50]}...")
        print(f"   期待: {case['expected']} | 検出: {detected} {status}")
        print()
    
    print("📁 制約ファイル読み込みテスト\n")
    
    domains = ["general", "medical", "legal", "engineering", "ai_ml", "cloud_devops", "safety_critical"]
    
    for domain in domains:
        try:
            constraints = load_domain_constraints(domain)
            length = len(constraints)
            print(f"✅ {domain}: {length}文字の制約を読み込み")
        except Exception as e:
            print(f"❌ {domain}: エラー - {e}")
    
    print("\n🎯 テスト完了")

if __name__ == "__main__":
    test_domain_detection()
