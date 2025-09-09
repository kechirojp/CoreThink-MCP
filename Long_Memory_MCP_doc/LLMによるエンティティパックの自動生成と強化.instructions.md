---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

# User-specific Entity Pack Evolution System
## 進化型エンティティパック システム実装プラン

### 🎯 コンセプト実装状況

✅ **完全透明バックエンド**
- ユーザーは「パック」という概念を一切意識しない
- save_memory / search_memories が内部で自動進化
- LLMが裏で学習・適応・個人化

✅ **段階的進化モデル**
```
初回セッション → デフォルト3パック使用
3-10セッション → 個人傾向学習開始  
10-50セッション → 専門パック1-2個生成
50+セッション → 高度個人化（5-7個専門パック）
```

✅ **user_id紐付け強化学習**
- 各ユーザーの使用パターン蓄積
- LLM推論による専門パック生成
- 継続使用による精度向上

### 🛠 技術実装アーキテクチャ

#### **コアファイル構成**
```
src/
├── auto_pack_detector.py        # 既存（基本検出）
├── user_pack_evolution.py       # 新規（進化管理）
├── llm_pack_generator.py        # 新規（LLM統合）
└── pack_integration.py          # 新規（MCP統合）

config/
├── pack_indicators.json         # 既存（デフォルトパック）
└── user_packs/                  # 新規（個人設定保存）
    ├── user_123abc.json
    ├── user_456def.json
    └── ...

user_packs/user_123abc.json 例:
{
  "user_id": "user_123abc",
  "evolution_stage": "specialized",
  "custom_packs": {
    "healthcare_pack": {...},
    "research_pack": {...}
  },
  "pack_usage_stats": {
    "dev_pack": 45,
    "healthcare_pack": 23,
    "lifelog_pack": 12
  }
}
```

#### **MCP統合ポイント**
```python
# main.py での透明統合

@app.post("/tools/save_memory")
async def save_memory_with_evolution(memory_in: MemoryIn, db: Session):
    """記憶保存 + 自動パック進化"""
    
    # 1. 進化型パック検出
    pack_result = await enhanced_detect_pack_with_evolution(
        user_id=memory_in.user_id,
        text=memory_in.raw_text,
        context={"source": "save_memory"}
    )
    
    # 2. メタデータ追加
    memory_in.metadata = memory_in.metadata or {}
    memory_in.metadata.update({
        "detected_pack": pack_result["primary_pack"],
        "confidence": pack_result["confidence"],
        "user_specialized": pack_result.get("user_specialized", False),
        "evolution_stage": pack_result["evolution"]["evolution_stage"]
    })
    
    # 3. 通常保存処理
    return await core_api.save_memory_endpoint(memory_in, db)

@app.post("/tools/search_memories") 
async def search_memories_with_evolution(request: MemorySearchRequest, db: Session):
    """検索 + 個人化パック適用"""
    
    # 1. 検索クエリの進化型パック判定
    pack_result = await enhanced_detect_pack_with_evolution(
        user_id=request.user_id,
        text=request.query,
        context={"source": "search_memories"}
    )
    
    # 2. ユーザー専用フィルタ適用
    if pack_result["confidence"] == "high":
        request.metadata_filter = {
            "detected_pack": pack_result["primary_pack"]
        }
    elif pack_result["user_specialized"]:
        # 個人化済みユーザーは関連パックも検索
        request.metadata_filter = {
            "detected_pack": {"$in": pack_result["packs_to_search"]}
        }
    
    # 3. 通常検索処理
    return await core_api.search_memories_endpoint(request, db)
```

### 🔄 進化トリガー設計

#### **新パック生成条件**
1. **専門用語の集中出現**: 既存パックで低信頼度が3回連続
2. **特定ドメインの高頻度**: 同一分野キーワードが10回以上
3. **セッション閾値**: 20セッション経過 + 個人パターン明確化

#### **パック改良条件**  
1. **キーワード追加**: 新語が5回以上出現 → 自動追加
2. **重み調整**: 使用頻度に基づく confidence_threshold 調整
3. **否定指標学習**: 誤分類パターンから negative_indicators 拡充

### 🧠 LLM統合戦略

#### **LLM推論プロンプト最適化**
```
【システムプロンプト】
あなたはユーザー専用エンティティパック生成の専門家です。
以下の原則を厳守してください：

1. 既存3パック（dev/work/lifelog）で分類困難な場合のみ新パック生成
2. 専門性の高い分野（医療、教育、金融等）に特化
3. 10-20個のキーワードで構成（high/medium分離）
4. negative_indicators で衝突回避
5. JSON形式で構造化回答

【入力】
- ユーザーの発言履歴
- 既存パック使用統計  
- 検出失敗パターン

【出力】
- 新パック定義（JSON）
- 生成理由説明
- 信頼度評価
```

#### **品質保証機構**
```python
def validate_generated_pack(pack_data: dict) -> bool:
    """LLM生成パックの品質検証"""
    
    # 1. スキーマ検証
    required_fields = ["id", "name", "high_confidence", "medium_confidence"]
    if not all(field in pack_data for field in required_fields):
        return False
    
    # 2. キーワード重複チェック
    existing_keywords = get_all_existing_keywords()
    new_keywords = pack_data["high_confidence"] + pack_data["medium_confidence"]
    overlap_ratio = len(set(new_keywords) & existing_keywords) / len(new_keywords)
    if overlap_ratio > 0.7:  # 70%以上重複なら却下
        return False
    
    # 3. 専門性チェック（簡易）
    if len(pack_data["high_confidence"]) < 5:
        return False
    
    return True
```

### 📊 統計・可視化

#### **進化状況ダッシュボード**
```python
@app.get("/api/user_evolution_stats")
async def get_user_evolution_stats(user_id: str):
    """ユーザー進化統計（開発者向け）"""
    
    profile = evolution_manager._load_user_profile(user_id)
    
    return {
        "user_id": user_id,
        "evolution_stage": profile.evolution_stage,
        "total_interactions": profile.total_interactions,
        "custom_packs_count": len(profile.custom_packs),
        "specialization_domains": profile.specialization_domains,
        "pack_usage_distribution": profile.pack_usage_stats,
        "average_confidence": sum(profile.confidence_history) / len(profile.confidence_history),
        "last_updated": profile.last_updated
    }
```

### 🚀 段階的展開計画

#### **Phase 3-B: 基盤実装（今週）**
1. ✅ `UserPackEvolutionManager` 実装完了
2. 🔄 `LLMPackGenerator` 実装
3. 🔄 既存 `AutoPackDetector` との統合
4. 🔄 基本テスト作成

#### **Phase 4: MCP統合（来週）**  
1. `save_memory` / `search_memories` 透明統合
2. user_id管理強化
3. LLM API統合（OpenAI/Claude）
4. エラーハンドリング + フォールバック

#### **Phase 5: 最適化（来月）**
1. パフォーマンス最適化（キャッシュ、非同期）
2. 進化アルゴリズム改良
3. 統計・分析機能
4. 運用監視・アラート

### 💡 実装のキーポイント

1. **透明性**: ユーザーは進化を意識しない
2. **安全性**: LLM失敗時は既存パックにフォールバック  
3. **効率性**: 過度な進化を避け、必要時のみ生成
4. **個人化**: user_idベースの完全分離
5. **品質**: 生成パックの検証・フィルタリング

この設計により、**数千職業への対応 + 完全透明 + 継続学習**が実現できます！
