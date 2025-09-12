# CoreThink-MCP Elicitation機能 技術文書

## 概要

CoreThink-MCP に FastMCP 2.10.0+ の User Elicitation 機能を統合しました。この機能により、ツール実行中にユーザーから段階的に情報を収集し、不完全な入力でも高度な推論タスクを実行可能になります。

## 機能仕様

### 1. Elicitation Handler (`src/corethink_mcp/elicitation.py`)

**主要クラス:**
- `CoreThinkElicitationHandler`: メインのハンドラークラス
- `ElicitationContext`: コンテキスト情報管理

**核心機能:**
- **自動パラメータ検出**: 不足パラメータの自動識別
- **文脈的質問生成**: CoreThink-MCP の推論機能と連携した質問強化
- **構造化応答**: FastMCP の型システムに対応した応答生成
- **会話履歴管理**: 継続的な対話コンテキスト保持

### 2. サーバー側統合

**修正ファイル:** `src/corethink_mcp/server/corethink_server.py`

**変更内容:**
- `refine_understanding` ツールの引数を Optional に変更
- `context_clues` パラメータにデフォルト値 `""` を設定
- Elicitation対応のためのコンテキスト処理追加

### 3. テストスイート (`test_elicitation.py`)

**テストシナリオ:**
1. **不完全パラメータテスト**: 意図的に一部パラメータを省略
2. **段階的収集テスト**: 複数パラメータの順次収集
3. **ワークフローテスト**: 実際の使用ケースでの動作確認

## 技術的優位性

### 1. CoreThink-MCP 固有の機能

```python
def _enhance_question_with_reasoning(self, original_message: str, elicit_context: ElicitationContext) -> str:
    """CoreThink-MCP の推論機能で質問を強化"""
    enhanced_message = f"""
【CoreThink-MCP インタラクティブ支援】

🎯 実行中のツール: {elicit_context.tool_name}
📋 現在のパラメータ: {len(elicit_context.current_params)}個設定済み
❓ サーバーからの要求: {original_message}

【推論コンテキスト】
{elicit_context.reasoning_context or "標準的な情報収集"}
```

### 2. ツール別の最適化

```python
tool_contexts = {
    'reason_about_change': '変更提案の安全性と妥当性を評価するための情報',
    'validate_against_constraints': '制約適合性を検証するための詳細情報',
    'execute_with_safeguards': '安全な実行のための実行計画情報',
    'refine_understanding': '曖昧性解消のための文脈情報',
    'trace_reasoning_steps': '推論過程の詳細度調整情報'
}
```

### 3. インテリジェントな応答構造化

- FastMCP のデータクラス型システムとの完全統合
- 型安全な応答生成
- フォールバック機能による堅牢性

## 実装上の工夫

### 1. エラーハンドリング

```python
try:
    # Elicitation処理
    structured_response = self._structure_response(user_input, response_type, elicit_context)
    return structured_response
except Exception as e:
    logger.error(f"Elicitation処理エラー: {str(e)}")
    return ElicitResult(action="cancel")
```

### 2. 会話履歴管理

- 最新100件の対話を保持
- タイムスタンプ付き詳細ログ
- ツール別コンテキスト追跡

### 3. ユーザー体験の向上

- 直感的な質問フォーマット
- 日本語/英語両対応
- キャンセル・スキップ機能

## 使用方法

### 1. 基本的な使用

```python
from fastmcp import Client
from src.corethink_mcp.elicitation import elicitation_handler

async with Client("corethink_server.py", elicitation_handler=elicitation_handler) as client:
    # 不完全なパラメータでツール呼び出し
    result = await client.call_tool("refine_understanding", {
        "ambiguous_request": "システムのパフォーマンスを向上させて"
        # context_clues と domain_hints は自動的に収集される
    })
```

### 2. 対話例

```
【CoreThink-MCP インタラクティブ支援】

🎯 実行中のツール: refine_understanding
📋 現在のパラメータ: 1個設定済み
❓ サーバーからの要求: context_clues が必要です

【推論コンテキスト】
曖昧性解消のための文脈情報

【推奨される回答】
- 具体的で実行可能な内容をお願いします
- 不明な場合は「不明」または「スキップ」と入力してください

あなたの回答: 対象はWebAPIのレスポンス時間改善、現在500ms、目標200ms以下
```

## 今後の拡張計画

### 1. GUI統合

- Web UI での視覚的な対話インターフェース
- ドラッグ&ドロップでのファイル指定
- リアルタイムプレビュー

### 2. AI支援強化

- GPT-4による質問生成最適化
- 過去の対話パターンからの学習
- 自動提案機能

### 3. エンタープライズ機能

- マルチユーザー対応
- 認証・認可システム統合
- 監査ログ機能

## まとめ

CoreThink-MCP の Elicitation 機能実装により、以下の価値を実現しました:

1. **ユーザビリティ向上**: 不完全な入力でも段階的に実行可能
2. **推論品質向上**: 必要な情報を的確に収集して高品質な推論実行
3. **競合優位性**: FastMCP 2.10.0+ 最新機能への対応
4. **拡張可能性**: 将来の AI 支援機能への基盤確立

この実装により、CoreThink-MCP は単なる推論エンジンから、インタラクティブな AI アシスタントへと進化しました。
