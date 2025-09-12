# CoreThink-MCP 自然対話型Elicitation ガイド

## 概要

CoreThink-MCPの改良されたelicitation機能により、ユーザーとAIエージェントの自然な対話セッション中に、必要な情報を違和感なく収集できるようになりました。

## 主要改善点

### 1. 自然な対話フロー

**従来の技術的なアプローチ:**
```
【CoreThink-MCP インタラクティブ支援】
🎯 実行中のツール: refine_understanding
📋 現在のパラメータ: 1個設定済み
❓ サーバーからの要求: 文脈手がかりを提供してください
```

**改良後の自然なアプローチ:**
```
🤔 理解を深めています...

「システムのパフォーマンスを向上させて」について、より詳しい状況や背景を教えてください。
例：どのようなシステムか、現在の状況、関連する制約など

💡 この情報により、より適切で安全な処理が可能になります。
```

### 2. セッション継続性の向上

- **視覚的な違和感を軽減**: 重いボーダーから軽い区切り線へ
- **AI Assistant らしいトーン**: 技術的すぎない、親しみやすい表現
- **自然な進行表示**: ツール固有のコンテキストアイコンと説明

### 3. ユーザー体験の最適化

#### 入力オプションの多様化
```python
# キャンセル・スキップの自然な表現
cancel_words = ['cancel', 'キャンセル', 'quit', 'exit']
skip_words = ['skip', 'スキップ', '不明', '後で', 'unknown']
```

#### フィードバックの即座性
```
✅ 回答を受け付けました: Webアプリケーション
⏭️ この項目をスキップします。
❌ 処理をキャンセルしました。
```

## 技術実装詳細

### 1. ツール別コンテキスト表示

```python
tool_contexts = {
    'reason_about_change': '🤔 変更内容を詳しく検討しています...',
    'validate_against_constraints': '🔍 安全性を確認しています...',
    'execute_with_safeguards': '⚡ 実行準備を進めています...',
    'refine_understanding': '💭 理解を深めています...',
    'trace_reasoning_steps': '🧠 推論プロセスを分析しています...'
}
```

### 2. 自然言語による情報要求

```python
# refine_understanding ツールでの改良
if not context_clues:
    context_clues = await ctx.request_user_input(
        f"「{ambiguous_request}」について、より詳しい状況や背景を教えてください。\n例：どのようなシステムか、現在の状況、関連する制約など",
        schema={"type": "string", "description": "文脈情報"}
    )
```

### 3. エラーハンドリングの改善

```python
try:
    user_input = input("💬 ").strip()
    print(f"✅ 回答を受け付けました: {user_input}")
    return user_input
except (EOFError, KeyboardInterrupt):
    print("\n❌ 入力がキャンセルされました。")
    return None
```

## 使用例: 自然な対話フロー

### シナリオ: システム最適化の要求

**1. 初期要求**
```
User: "システムのパフォーマンスを向上させて"
AI: refine_understanding ツールを実行します
```

**2. 自然な情報収集**
```
🤔 理解を深めています...

「システムのパフォーマンスを向上させて」について、より詳しい状況や背景を教えてください。
例：どのようなシステムか、現在の状況、関連する制約など

💬 Webアプリケーションの応答速度が遅くて困っています
✅ 回答を受け付けました: Webアプリケーションの応答速度が遅くて困っています
```

**3. 専門分野の確認**
```
この内容はどの分野に関連しますか？
例：技術・開発、医療、法律、ビジネス、一般

💬 技術・開発
✅ 回答を受け付けました: 技術・開発
```

**4. 推論結果の提供**
```
AI: 分析が完了しました。Webアプリケーションの応答速度改善について、
    以下の観点から具体的な最適化計画を提案します...
```

## FastMCP 2.12.2 統合のベストプラクティス

### 1. ElicitResult の適切な使用

```python
# 明示的な制御が必要な場合
return ElicitResult(action="accept", content=response_data)
return ElicitResult(action="decline")  # 情報提供を辞退
return ElicitResult(action="cancel")   # 全体をキャンセル

# 簡潔な場合（推奨）
return response_data  # FastMCP が自動的に accept として処理
```

### 2. 型安全性の確保

```python
# FastMCP の dataclass 自動変換を活用
if hasattr(response_type, '__dataclass_fields__'):
    fields = response_type.__dataclass_fields__
    if 'value' in fields:
        return response_type(value=user_input)
```

### 3. エラー境界の明確化

```python
try:
    structured_response = self._structure_response(user_input, response_type, elicit_context)
    return structured_response
except Exception as e:
    logger.error(f"Elicitation処理エラー: {str(e)}")
    return ElicitResult(action="cancel")
```

## 今後の拡張予定

### 1. GUI統合
- VS Code Webview での対話インターフェース
- リアルタイムな入力検証とサジェスト

### 2. 多言語対応
- 英語/日本語の自動切り替え
- 文化的コンテキストの考慮

### 3. 学習機能
- ユーザーの回答パターンの記憶
- パーソナライズされた質問生成

## まとめ

この改良により、CoreThink-MCPのelicitation機能は技術的な詳細を隠蔽し、ユーザーとAIエージェントの自然な対話の一部として機能するようになりました。セッションの中断感を最小限に抑え、必要な情報を効率的に収集することで、より高度で安全な推論処理を実現します。
