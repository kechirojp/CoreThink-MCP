## GSRの「言語内推論」を活かすための具体的ツール設計例

### 🧠 GSRの核心思想とMCPツール設計

GSRは「自然言語→形式論理→自然言語」の変換ロスを避け、**自然言語のまま制約適用・推論・説明**を行います。

### 📝 具体的ツール設計例

#### 1. `reason_about_change` - GSR中核ツール
```python
@mcp.tool()
async def reason_about_change(
    user_intent: str,  # "このバグを直したい"
    current_state: str,  # "tests/test_calc.py::test_divide_zero が失敗"
    proposed_action: str  # "ZeroDivisionError→ValueErrorに変更"
) -> str:
    """
    GSRの自然言語推論を実行。制約・前提・矛盾を言語のまま評価。
    
    Returns: 自然言語の推論結果
    """
    return """
    【推論過程】
    1. 意図分析: エラー型の統一化が目的
    2. 制約確認: 公開API変更は禁止 → この変更は内部例外型のみ → OK
    3. 影響推定: 呼び出し側のtry-except文に影響 → 要確認
    4. 矛盾検出: なし
    
    【判定】PROCEED_WITH_CAUTION
    【理由】API互換性は保たれるが、例外処理の変更は慎重に
    【推奨】まず失敗テストのみで確認、その後近傍テストを実行
    """
```

#### 2. `trace_reasoning_steps` - 逐語トレース
```python
@mcp.tool()
async def trace_reasoning_steps(
    context: str,  # 現在の状況説明
    step_description: str  # 実行予定のステップ
) -> str:
    """
    GSRの逐語トレースを生成。各推論ステップを言語で記録。
    """
    return """
    【トレース記録】
    時刻: 2025-01-27 10:30
    前提: テストtest_divide_zeroが失敗、ZeroDivisionError期待
    制約: 公開API変更禁止、最小変更原則
    ステップ: ValueError→ZeroDivisionErrorに変更を検討
    判定: 制約「最小変更」に適合、API変更なし
    次段階: パッチ生成→検証→適用
    信頼度: HIGH（明確な制約適合）
    """
```

#### 3. `refine_understanding` - 曖昧性解消
```python
@mcp.tool()
async def refine_understanding(
    ambiguous_request: str,  # "パフォーマンスを改善して"
    context_clues: str  # ファイル情報、エラーログなど
) -> str:
    """
    曖昧な要求を具体的な実行可能タスクに変換（GSRの曖昧性同定）
    """
    return """
    【曖昧性分析】
    「パフォーマンス改善」の候補:
    1. 実行速度向上（アルゴリズム最適化）
    2. メモリ使用量削減
    3. I/O効率化
    
    【文脈からの推定】
    - ログにO(n²)の警告 → 実行速度が主要課題
    - 大量データ処理関数 → アルゴリズム最適化
    
    【具体化されたタスク】
    「計算複雑度をO(n²)からO(n log n)に改善する」
    制約: 出力結果の完全一致、公開API保持
    """
```

## Phase 1の詳細範囲

### 🎯 最小限の実行可能セット（MVP）

#### **必須ツール（3つのみ）**

```python
# 1. 推論エンジン（GSRの中核）
reason_about_change(user_intent, current_state, proposed_action) -> reasoning_text

# 2. 制約検証（安全性確保）
validate_against_constraints(proposed_change, reasoning_context) -> validation_text

# 3. 実行制御（段階的適用）
execute_with_safeguards(action_description, dry_run=True) -> execution_report
```

#### **必須リソース（2つのみ）**
```python
# constraints/current - 現在の制約ルール
# logs/reasoning_trace - 推論過程の記録
```

#### **Phase 1で実装しないもの**
```bash
❌ MLflow連携（検証は手動）
❌ Prefectワークフロー（シンプルな順次実行）
❌ 複雑なタスク分類（簡易ルールベース）
❌ Node.js版（Python STDIO のみ）
❌ 高度な制約学習（固定ルールで開始）
```

### 📋 Phase 1実装チェックリスト

```markdown
### Week 1: 基盤
- [ ] uv環境 + MCP SDK
- [ ] FastMCPサーバ骨格
- [ ] constraints.txtの読み書き
- [ ] ロギング設定（stderr only）

### Week 2: 中核ツール
- [ ] reason_about_change実装
- [ ] validate_against_constraints実装  
- [ ] 自然言語ベースの入出力設計

### Week 3: 実行・テスト
- [ ] execute_with_safeguards実装
- [ ] git操作の隔離（worktree）
- [ ] Claude Desktop接続テスト

### Week 4: 統合・検証
- [ ] VSCode + Copilot接続
- [ ] 基本的な使用例で動作確認
- [ ] Phase 2準備（追加ツール設計）
```

## ツール設計のシンプル化修正例

### ❌ **修正前（過度に構造化）**
```python
@mcp.tool()
async def validate_patch(code: str, explanation: str, diff: str) -> str:
    return json.dumps({
        "success": False,
        "score": 0.75,
        "violations": {
            "MUST": ["API変更検出"],
            "NEVER": ["デバッグ出力残存"],
            "SHOULD": ["docstring更新推奨"]
        },
        "suggestions": ["制約追加候補A", "制約追加候補B"],
        "trace": "detailed_log..."
    })
```

### ✅ **修正後（GSR言語内推論）**
```python
@mcp.tool()
async def validate_against_constraints(
    proposed_change: str,  # 自然言語での変更説明
    reasoning_context: str  # reason_about_changeの出力
) -> str:
    """GSRの言語内制約検証"""
    return """
    【制約検証結果】
    
    提案変更: 「ZeroDivisionError を ValueError に変更」
    
    制約適合性:
    ✅ MUST「公開API変更禁止」→ 内部例外型のみ変更、適合
    ❌ NEVER「テスト期待値変更禁止」→ test_divide_zero修正必要、違反
    ⚠️ SHOULD「最小変更原則」→ 2ファイル修正、境界線
    
    総合判定: VIOLATION_DETECTED
    
    違反理由: テストファイルの期待値変更が発生
    推奨対応: 
    1. ValueError→ZeroDivisionErrorは正しい修正方向
    2. ただし例外メッセージも統一検討
    3. 段階的適用: コード修正→テスト修正→統合確認
    
    次のステップ: テスト修正も含めた完全な変更案の再検討
    """
```

### 🔄 **設計原則の変化**

| 項目 | 修正前 | 修正後（GSR準拠） |
|------|--------|------------------|
| **出力形式** | JSON構造 | 自然言語のまま |
| **エラー表現** | `{"success": false}` | `❌ 違反理由: ...` |
| **推論過程** | `"trace"` フィールド | 推論ステップを文章で展開 |
| **制約表現** | `["API変更検出"]` | `✅ MUST「公開API変更禁止」→ 適合` |
| **次のアクション** | `"suggestions"` 配列 | `推奨対応: 1. ... 2. ...` |

### 🎯 **修正のメリット**

1. **可読性**: ホスト（Claude/Copilot）が内容を理解しやすい
2. **拡張性**: 制約が複雑化しても自然言語で表現可能
3. **デバッグ**: 推論過程が人間にとって追跡しやすい
4. **GSR準拠**: 「翻訳ロス」なしの言語内推論を実現

### 🔧 **実装の具体的変更点**

```python
# 修正前: 構造化重視
def validate(self, code, explanation, diff):
    violations = []
    if self.check_api_change(code):
        violations.append("API_CHANGE")
    return {"violations": violations}

# 修正後: 言語内推論
def validate_with_reasoning(self, proposed_change, context):
    reasoning = f"""
    【分析対象】{proposed_change}
    【文脈】{context}
    
    【制約確認過程】
    公開API変更チェック: {self.explain_api_check(proposed_change)}
    最小変更原則チェック: {self.explain_minimal_change(proposed_change)}
    
    【結論】{self.synthesize_judgment()}
    """
    return reasoning
```

この設計により、MCPツールがGSRの「自然言語のまま推論」思想を保ちながら、実用的な制約検証・実行制御を提供できます。