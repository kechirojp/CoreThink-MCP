# FastMCP プロジェクト詳細分析報告書

## 📊 プロジェクト深層理解

### 🎯 CoreThink-MCP プロジェクト概要

**基本構成:**
- **論文基盤**: CoreThink論文のGeneral Symbolics Reasoning (GSR)を実装
- **フレームワーク**: FastMCP v2.0採用（公式推奨Pythonライブラリ）
- **アーキテクチャ**: MCP Server + Client 統合エコシステム
- **特化領域**: ツール呼び出し、コード生成、プランニングの3領域

**技術的優位性:**
1. **GSR統合**: 学術論文ベースの推論エンジン（公式例に無い独自性）
2. **サンドボックス実行**: git worktreeによる安全な変更適用
3. **制約駆動設計**: constraints.txtによる動的制約システム
4. **マルチTransport**: STDIO/HTTP両対応

### 🛠 実装済み機能

**MCPツール (9個):**
- `reason_about_change`: GSR推論による変更評価
- `validate_against_constraints`: 制約検証
- `execute_with_safeguards`: サンドボックス実行
- `trace_reasoning_steps`: 推論トレース（Section 5.3準拠）
- `refine_understanding`: 曖昧性解消（Section 5.1準拠）
- `detect_symbolic_patterns`: ARC-AGI-2原子操作
- `orchestrate_multi_step_reasoning`: 複数段階推論統制
- `analyze_repository_context`: リポジトリ分析
- `learn_dynamic_constraints`: 動的制約学習

**MCPリソース:**
- `file://constraints`: 制約ファイル読み取り
- `file://reasoning_log`: 推論ログアクセス

## 🔍 FastMCP 詳細機能分析

### 📚 FastMCP Documentation Links（30分ごと更新推奨）

1. **クライアント機能:**
   - https://gofastmcp.com/clients/client - 基本クライアント操作
   - https://gofastmcp.com/clients/transports - 接続方式詳細
   - https://gofastmcp.com/clients/tools - ツール実行機能
   - https://gofastmcp.com/clients/resources - リソースアクセス
   - https://gofastmcp.com/clients/prompts - プロンプトテンプレート

2. **高度機能:**
   - https://gofastmcp.com/clients/elicitation - **ユーザー誘発機能**
   - https://gofastmcp.com/clients/progress - 進捗モニタリング
   - https://gofastmcp.com/clients/sampling - LLMサンプリング要求
   - https://gofastmcp.com/clients/roots - ローカルコンテキスト提供

3. **統合機能:**
   - https://gofastmcp.com/integrations/mcp-json-configuration - 設定管理

## 🎯 重要発見: Elicitation 機能

### 📖 Elicitation とは？

**定義**: MCPサーバーがツール実行中に構造化されたユーザー入力を要求する機能
- **目的**: 事前にすべての入力を要求せず、必要に応じてインタラクティブに情報収集
- **用途例**: 
  - ファイル管理ツール: "どのディレクトリを作成しますか？"
  - データ分析ツール: "どの日付範囲を分析しますか？"

### 🔧 FastMCP での Elicitation 実装詳細

**1. クライアント側ハンドラー:**
```python
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

async def elicitation_handler(message: str, response_type: type, params, context):
    # ユーザーにメッセージを表示して入力を収集
    user_input = input(f"{message}: ")
    
    # FastMCPが提供するdataclassタイプを使用してレスポンス作成
    response_data = response_type(value=user_input)
    
    # データを直接返す（暗黙的にaccept）
    return response_data
    
    # または明示的制御用
    # return ElicitResult(action="accept", content=response_data)

client = Client(
    "my_mcp_server.py",
    elicitation_handler=elicitation_handler,
)
```

**2. ハンドラーパラメータ:**
- `message: str` - ユーザーに表示するプロンプトメッセージ
- `response_type: type` - FastMCPが JSON スキーマから生成したPython dataclass型
- `params: ElicitRequestParams` - 元のMCP誘発リクエストパラメータ
- `context: RequestContext` - リクエストコンテキストメタデータ

**3. レスポンスアクション:**
- `accept`: ユーザーが有効な入力を提供（contentフィールド必須）
- `decline`: ユーザーが情報提供を拒否（content省略）
- `cancel`: ユーザーが操作全体をキャンセル（content省略）

## 🚀 CoreThink-MCP への Elicitation 統合提案

### 💡 実装アイデア: 誘発型推論システム

**コンセプト**: ユーザーが「corethinking使って分析お願い」と書いたら即座にツール起動・分析開始

**実装戦略:**

1. **自動ツール選択機能**: 
   - ユーザーの自然言語入力から適切なツールを推論
   - `refine_understanding` → `reason_about_change` → `validate_against_constraints` のフロー自動化

2. **インタラクティブ補完機能**:
   - 不足パラメータをelicitationで動的収集
   - 例: "分析対象は？" "制約条件は？" "実行レベルは？"

3. **ワンクリック実行システム**:
   - 事前設定されたプロファイルに基づく自動実行
   - ユーザー確認を最小限に抑制

### 🛠 実装ステップ

**Phase 1: 基本 Elicitation ハンドラー実装**
```python
# CoreThink-MCP 拡張実装
@app.tool()
async def interactive_analysis(
    user_request: str,
    ctx: Context
) -> str:
    # Elicitation を使って不足情報を収集
    target = await ctx.elicit("分析対象を教えてください:", {"type": "string"})
    constraints = await ctx.elicit("制約条件はありますか？:", {"type": "string", "optional": True})
    
    # 自動的に適切なツールチェーン実行
    understanding = await refine_understanding(user_request, target, "")
    reasoning = await reason_about_change(user_request, target, understanding)
    validation = await validate_against_constraints(reasoning, constraints or "")
    
    return f"分析完了:\n{understanding}\n{reasoning}\n{validation}"
```

**Phase 2: 自動ツール選択**
```python
async def smart_tool_dispatcher(user_input: str, ctx: Context):
    # 自然言語解析による適切なツール選択
    if "曖昧" in user_input or "明確" in user_input:
        return await refine_understanding(user_input, "", "")
    elif "分析" in user_input or "推論" in user_input:
        return await reason_about_change(user_input, "", "")
    elif "実行" in user_input or "適用" in user_input:
        return await execute_with_safeguards(user_input, True)
    else:
        # Elicitation で意図を確認
        intent = await ctx.elicit("何をしたいですか？", {
            "type": "string",
            "enum": ["曖昧性解消", "推論分析", "安全実行", "その他"]
        })
        # 選択に基づく分岐処理
```

**Phase 3: ワンコマンド実行システム**
```python
@app.tool()
async def corethink_auto(
    request: str = "分析お願い",
    auto_mode: bool = True
) -> str:
    """
    CoreThink 自動分析システム
    ユーザーが「corethinking使って分析お願い」と言ったら即座に実行
    """
    if auto_mode:
        # 事前設定プロファイルに基づく自動実行
        return await auto_analysis_pipeline(request)
    else:
        # インタラクティブモード
        return await interactive_analysis_pipeline(request)
```

## 📋 実装要件

### 🎯 成功基準
- **即応性**: ユーザー入力から3秒以内でツール起動
- **直感性**: 技術的知識不要での操作可能
- **安全性**: 既存の制約システムとの完全統合
- **拡張性**: 新しいツールとの自動連携

### 🛡 制約事項
- constraints.txtの完全遵守
- STDIO/HTTPトランスポート両対応
- 既存9ツールとの後方互換性
- 自然言語出力フォーマット維持

## 🔄 次ステップ

1. **Elicitation基本実装** (1-2日)
2. **自動ツール選択ロジック** (2-3日) 
3. **ワンコマンドシステム統合** (1-2日)
4. **テスト・最適化** (1-2日)

**推定実装期間**: 5-9日
**優先度**: High（ユーザビリティ大幅改善）

---

*この分析は CoreThink-MCP プロジェクトの deep understanding と FastMCP elicitation 機能の詳細調査に基づく。*
