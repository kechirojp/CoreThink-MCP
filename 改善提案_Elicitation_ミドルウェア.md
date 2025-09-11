# CoreThink-MCP 改善提案：Elicitation & ミドルウェア

## 📋 現状分析

### Elicitation実装状況
- ❌ **分離型アーキテクチャ**: 独立したハンドラー実装
- ❌ **メインサーバー未統合**: 実際の動的パラメータ収集なし
- ❌ **FastMCP標準違反**: `ctx.elicit()`パターン未採用
- ❌ **ユーザビリティ低下**: リアルタイム情報収集不可

### ミドルウェア現状
- ❌ **ミドルウェアなし**: 各ツールで重複処理
- ❌ **非統一アーキテクチャ**: エラーハンドリングとログが散在
- ❌ **FastMCP機能未活用**: パイプライン処理なし

## 🎯 改善ロードマップ

### Phase 1: Elicitation再実装（優先度：高）

#### Before（現在の問題実装）
```python
# ❌ 分離されたハンドラー（elicitation.py）
class CoreThinkElicitationHandler:
    async def handle_elicitation(self, message, params, context):
        # 複雑な外部処理...

# ❌ メインツールで使えない
@app.tool()
async def refine_understanding(
    ambiguous_request: str,
    context_clues: str = "",  # can be elicited if missing ←コメントのみ
    domain_hints: str = ""   # can be elicited if missing ←実装なし
):
```

#### After（FastMCP標準実装）
```python
# ✅ FastMCP標準パターン
from dataclasses import dataclass
from fastmcp.client.elicitation import elicit

@dataclass
class RefinementData:
    context_clues: str
    domain_hints: str
    specific_requirements: str

@app.tool()
async def refine_understanding(
    ctx: Context,
    ambiguous_request: str,
    context_clues: str = "",
    domain_hints: str = ""
):
    # 不足情報の動的収集
    if not context_clues or not domain_hints:
        missing_data = await ctx.elicit(
            message=f"'{ambiguous_request}'について追加情報が必要です",
            response_type=RefinementData
        )
        context_clues = missing_data.context_clues
        domain_hints = missing_data.domain_hints
    
    # 推論処理...
```

### Phase 2: ミドルウェア導入（優先度：中高）

#### CoreThink専用ミドルウェア設計

```python
# 1. 制約検証ミドルウェア
class ConstraintValidationMiddleware:
    async def on_call_tool(self, request, context):
        # constraints.txt チェック
        constraints = await load_constraints()
        if not validate_against_constraints(request, constraints):
            raise ConstraintViolationError()

# 2. 推論ログミドルウェア  
class ReasoningLogMiddleware:
    async def on_call_tool(self, request, context):
        context.reasoning_log = []
    
    async def on_tool_result(self, result, context):
        await log_reasoning_process(context.reasoning_log)

# 3. セーフ実行ミドルウェア
class SafeExecutionMiddleware:
    async def on_call_tool(self, request, context):
        if requires_sandbox(request):
            context.sandbox_mode = True
            setup_sandbox_environment()
```

#### 統合サーバー実装
```python
from fastmcp import FastMCP
from fastmcp.middleware import LoggingMiddleware, TimingMiddleware

app = FastMCP("corethink-mcp")

# ミドルウェアパイプライン構築
app.add_middleware(LoggingMiddleware())
app.add_middleware(TimingMiddleware())
app.add_middleware(ConstraintValidationMiddleware())
app.add_middleware(ReasoningLogMiddleware())
app.add_middleware(SafeExecutionMiddleware())

# 各ツールはビジネスロジックのみ集中
@app.tool()
async def reason_about_change(ctx: Context, change_description: str):
    # 制約チェック、ログ、セキュリティは自動処理
    # 推論ロジックのみ実装
```

### Phase 3: 既存ツール最適化（優先度：中）

#### リファクタリング対象
1. `reason_about_change` - Elicitation統合
2. `validate_against_constraints` - ミドルウェア化
3. `execute_with_safeguards` - ミドルウェア統合
4. `refine_understanding` - 完全なElicitation実装

## 📊 期待される効果

### Elicitation改善効果
- ✅ **ユーザビリティ向上**: リアルタイム情報収集
- ✅ **型安全性**: データクラスによる構造化入力
- ✅ **マルチターン対話**: 段階的な情報収集
- ✅ **FastMCP標準準拠**: 保守性・拡張性向上

### ミドルウェア導入効果
- ✅ **コード重複排除**: DRY原則の徹底
- ✅ **一貫性確保**: 統一されたエラーハンドリング・ログ
- ✅ **保守性向上**: 関心の分離によるクリーンアーキテクチャ
- ✅ **拡張性確保**: 新機能追加の容易さ

## 🛠 実装計画

### Week 1: Elicitation再実装
1. 既存`elicitation.py`の分析・廃止検討
2. FastMCP標準パターンへの移行
3. `refine_understanding`での実装検証

### Week 2-3: ミドルウェア導入
1. 基本ミドルウェア（Logging, Timing）
2. CoreThink専用ミドルウェア（Constraint, Reasoning, Safety）
3. 既存ツールの段階的移行

### Week 4: 統合テスト・最適化
1. 全体統合テスト
2. パフォーマンス最適化
3. ドキュメント更新

## 🎯 結論

**Elicitation**: 現在の実装は確実に「中途半端で残念」。FastMCP標準への移行が急務。
**ミドルウェア**: CoreThink-MCPのアーキテクチャニーズに完璧に適合。導入を強く推奨。

これらの改善により、CoreThink-MCPは真の意味でモダンなMCPサーバーとして生まれ変わる。
