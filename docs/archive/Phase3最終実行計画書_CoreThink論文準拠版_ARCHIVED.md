# Phase3最終実行計画書：CoreThink論文準拠版

> **ユーザーレビューとCoreThink論文に基づく最終実装計画**  
> 作成日: 2025年9月11日  
> 基準: CoreThink論文精神 + 土倉氏指摘 + ユーザーレビュー

---

## 🎯 実行計画の基本方針

### 設計哲学
- **CoreThink論文忠実性**: 推論トレース・理解深化・多段階推論を重視
- **実用的バランス**: 機能性と簡潔性の適切なバランス
- **人間検証重視**: 推論過程記録による透明性確保
- **段階的改善**: 既存機能を破壊せず品質向上

### 削除vs維持の判断基準
1. **CoreThink論文の3ユースケース**（Tool-Calling, Code Generation, Planning）に直接貢献するか
2. **推論の透明性・解釈可能性**に必要不可欠か
3. **人間による検証・監査**に価値があるか
4. **独立機能として**明確な責任を持つか

---

## 📋 ツール削除・統合・維持計画

### ✅ **維持・統合ツール（6個）**

#### 1. trace_reasoning_steps（+ reason_about_change統合）
**統合理由**: CoreThink論文の「verbatim reasoning traces」が最重要
```python
async def trace_reasoning_steps(
    context: str,
    step_description: str,
    user_intent: str = "",          # reason_about_change統合
    current_state: str = "",        # reason_about_change統合
    proposed_action: str = "",      # reason_about_change統合
    reasoning_depth: str = "standard",
    ctx = None
) -> str:
    """
    推論ステップの詳細トレース + 変更判定の統合ツール
    
    CoreThink論文の「verbatim reasoning traces」「human-interpretable」を実装
    """
```

#### 2. validate_against_constraints
**維持理由**: 制約遵守はCoreThink論文の基本要件
```python
async def validate_against_constraints(
    proposed_change: str,
    reasoning_context: str = "",
    ctx = None
) -> str:
    """制約解釈の詳細分析による適合性検証"""
```

#### 3. execute_with_safeguards  
**維持理由**: 安全実行は論文の実用性要件
```python
async def execute_with_safeguards(
    action_description: str,
    dry_run: bool = True,
    ctx = None
) -> str:
    """サンドボックス実行 + リスク予測分析"""
```

#### 4. refine_understanding
**維持理由**: 論文の「ambiguity identification」「semantic preservation」
```python
async def refine_understanding(
    ambiguous_request: str,
    context_clues: str = "",
    domain_hints: str = "",
    ctx = None
) -> str:
    """理解深化による曖昧性解決"""
```

#### 5. orchestrate_multi_step_reasoning
**維持理由**: 論文のPlanningユースケースの核心機能
```python
async def orchestrate_multi_step_reasoning(
    task_description: str,
    available_tools: str,
    conversation_history: str = "",
    ctx = None
) -> str:
    """多段階推論による複雑タスク分解"""
```

#### 6. 内部推論記録機能（エンドポイント化せず）
**実装理由**: ユーザーレビューの「人間による検証」要件
```python
# MCPツールとしては公開せず、内部機能として実装
async def _log_reasoning_process(tool_name: str, inputs: dict, outputs: str, ctx=None):
    """推論過程の内部記録（人間検証用）"""
```

### ❌ **削除ツール（6個）**

#### 完全削除（CoreThink論文に言及なし）
```python
❌ detect_symbolic_patterns       # ARC-AGI-2特化、CoreThink範囲外
❌ analyze_repository_context     # SWE-Bench特化、CodeGen内で処理
❌ learn_dynamic_constraints      # 静的制約管理で十分
❌ get_reasoning_history          # 内部記録機能で代替
❌ get_history_statistics         # 同上
❌ manage_feature_flags           # YAML設定で十分
```

---

## 🎯 GSR（General Symbolics Reasoning）実装戦略

### CoreThink論文準拠の基本原則
- **堅牢な自然言語推論**: データ変換繰り返し問題を回避したNL-to-NL推論
- **GSRフレームワーク**: Native Language Processing + In-Language Reasoning
- **Verbatim Reasoning Traces**: 人間解釈可能な推論過程の完全記録
- **Context Preservation**: 自然言語の文脈・ニュアンスを完全保持
- **最小限Sampling**: 構造化推論の品質確認のみ（推論委託禁止）

### ツール別GSR実装仕様

#### 1. trace_reasoning_steps（統合後）

**GSR推論プロセス**:
```python
# CoreThink論文準拠：構造化自然言語推論
def gsr_reasoning_trace(context, step_description, proposed_action=""):
    """
    GSRフレームワーク：Native Language Processing
    - 自然言語のまま推論実行
    - データ変換なし
    - Verbatim Reasoning Traces
    """
    
    # Stage 1: Native Language Parsing & Semantic Preservation
    reasoning_trace = f"""
    【GSR推論分析】
    入力: {step_description}
    文脈: {context}
    提案: {proposed_action if proposed_action else '分析のみ'}
    
    【In-Language Reasoning Architecture】
    1. 制約パターン分析: {analyze_constraint_patterns(step_description)}
    2. 論理的一貫性確認: {verify_logical_consistency(context, step_description)}
    3. 前提条件検証: {validate_assumptions(step_description)}
    4. 実行可能性評価: {assess_feasibility(proposed_action)}
    5. リスク要因特定: {identify_risks(proposed_action)}
    
    【Verbatim Reasoning Traces】
    推論過程: [構造化された自然言語推論の詳細記録]
    """
    
    # 最小限品質確認（推論委託ではない）
    if ctx and enable_minimal_verification:
        simple_check = await ctx.sample(
            query="上記GSR推論に明らかな見落としがあれば一言で指摘",
            temperature=0.1, max_tokens=50
        )
    
    return reasoning_trace
```

**GSR品質向上効果**:

- 自然言語推論精度向上（目標：GSR原則100%遵守）
- データ変換問題回避（目標：NL-to-NL推論100%）
- 推論透明性確保（目標：Verbatim Traces完全記録）

#### 2. validate_against_constraints

**何をサンプリング**:
```python
# 制約解釈の詳細分析
sampling_query = f"""
【制約適合性詳細分析】
制約文書: {constraints}
提案変更: {proposed_change}

以下を詳細分析してください：
1. 各制約項目への適合状況
2. 見落としがちな制約違反の有無
3. グレーゾーンの判定理由
4. 制約回避のための修正案
5. 将来的制約抵触リスク

保守的観点で分析し、具体的根拠を示してください。
"""
```

**何に活かす**:
- 制約違反見落とし率削減（目標：30%削減）
- 制約解釈精度向上（目標：判定精度25%向上）
- グレーゾーン判定の明確化（目標：曖昧判定50%削減）

#### 3. execute_with_safeguards

**何をサンプリング**:
```python
# 実行前リスク分析
sampling_query = f"""
【実行前リスク評価】
実行アクション: {action_description}
現在状態: {current_state}

以下のリスクを評価してください：
1. セキュリティリスク（認証・認可・データ漏洩）
2. システムリスク（性能・可用性・整合性）  
3. データリスク（破損・消失・不整合）
4. 運用リスク（復旧不可・監査証跡・コンプライアンス）
5. 緊急停止条件と対策

リスクレベル（高・中・低）と具体的対策を提示してください。
"""
```

**何に活かす**:
- リスク予測精度向上（目標：25%向上）
- セキュリティ問題予防（目標：脆弱性検出率40%向上）
- 実行前安全確認強化（目標：事故率60%削減）

#### 4. refine_understanding

**何をサンプリング**:
```python
# 理解深化のための曖昧性分析
sampling_query = f"""
【理解深化分析】
曖昧な要求: {ambiguous_request}
利用可能コンテキスト: {context_clues}

以下を分析してください：
1. 曖昧性の原因（用語・前提・スコープ・優先度）
2. 推論による補完可能性
3. 複数解釈の可能性と影響
4. 追加確認が必要な要素
5. 推奨される解釈とその根拠

不確実性を明示し、確信度も含めて回答してください。
"""
```

**何に活かす**:
- 曖昧性解決率向上（目標：35%向上）
- 誤解釈防止（目標：解釈ミス40%削減）
- 要求明確化支援（目標：追加質問精度50%向上）

#### 5. orchestrate_multi_step_reasoning

**何をサンプリング**:
```python
# 多段階タスク分解の最適化
sampling_query = f"""
【多段階推論最適化】
複雑タスク: {task_description}
利用可能ツール: {available_tools}

以下を分析してください：
1. タスク分解の最適戦略
2. 実行順序の依存関係
3. 並列実行可能性
4. 失敗時の回復戦略
5. 効率化のボトルネック

実行可能な具体的計画として提示してください。
"""
```

**何に活かす**:
- タスク分解精度向上（目標：最適解発見率30%向上）
- 実行効率改善（目標：処理時間20%短縮）
- 失敗回復率向上（目標：回復成功率45%向上）

---

## 📊 成果測定指標

### 定量指標
| ツール | 測定指標 | 現在値 | 目標値 | 測定方法 |
|--------|---------|--------|--------|----------|
| trace_reasoning_steps | 推論盲点発見率 | - | +30% | テストケース評価 |
| validate_against_constraints | 制約違反見落とし率 | - | -30% | 制約テスト |
| execute_with_safeguards | リスク予測精度 | - | +25% | シミュレーション |
| refine_understanding | 曖昧性解決率 | - | +35% | 解釈テスト |
| orchestrate_multi_step_reasoning | タスク分解精度 | - | +30% | 複雑タスク評価 |

### 定性指標
- 推論過程の透明性向上
- ユーザーの信頼度向上
- デバッグ・監査の容易性向上
- 学習・改善サイクルの高速化

---

## 🚀 実装ステップ

### Phase 1: 削除・統合作業（1週間）
1. **削除対象6ツールの除去**
   - detect_symbolic_patterns, analyze_repository_context
   - learn_dynamic_constraints, get_reasoning_history
   - get_history_statistics, manage_feature_flags

2. **trace_reasoning_steps + reason_about_change統合**
   - 新しい統合インターフェース設計
   - 既存機能の移行とテスト

3. **設定ファイル簡素化**
   - feature_flags.yamlの必要最小限化
   - 不要設定の削除

### Phase 2: Sampling統合（1週間）
1. **各ツールのSampling仕様実装**
   - 上記詳細仕様に基づく実装
   - フォールバック機能の確保

2. **内部推論記録機能**
   - エンドポイント化しない内部機能
   - 人間検証用ログ出力

3. **品質向上の検証**
   - 各種テストケースでの効果測定
   - パフォーマンス影響評価

### Phase 3: 検証・調整（1週間）
1. **統合テスト**
   - 6ツール間の連携確認
   - エラーハンドリング検証

2. **品質測定**
   - 定量指標の初期測定
   - 改善効果の確認

3. **ドキュメント更新**
   - ユーザー向け説明書
   - 開発者向け仕様書

---

## 🎯 期待される成果

### 技術的成果
- **MCPツール数**: 12個 → 6個（50%削減）
- **設定項目数**: 15+ → 5個（67%削減）
- **推論品質向上**: 各ツールで25-40%の改善
- **透明性向上**: 推論過程の完全記録

### 運用的成果
- **VS CodeのMCPツール欄**: クリーンな表示
- **トークン効率**: 無駄なエンドポイント削除
- **保守性**: 適度な複雑性で機能性確保
- **ユーザー体験**: 透明で信頼できる推論

### 戦略的成果
- **CoreThink論文精神の実現**: 真の推論システム
- **土倉氏指摘への対応**: 目的明確な機能拡張
- **段階的改善基盤**: 将来拡張への礎

## 結論

この実行計画により、CoreThink-MCPは真にCoreThink論文の精神を体現し、土倉氏の指摘する「目的地のある鉄道敷設」を実現します。推論の透明性・解釈可能性を確保しながら、実用的なバランスを保った設計です。
