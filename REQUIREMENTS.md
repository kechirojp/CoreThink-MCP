# CoreThink-MCP 要件定義仕様書

## 📄 プロジェクト概要

### 🎯 目的
**CoreThink論文（General Symbolics Reasoning: GSR）**の思想を実装し、LLMが自然言語のまま推論・制約検証・安全実行を行えるMCPサーバーを構築する。

### 🔑 核心価値
- **自然言語内推論**: JSON構造化せず、言語のまま推論過程を保持
- **安全な変更適用**: サンドボックス環境での段階的実行
- **制約駆動開発**: constraints.txtによるルールベース検証
- **MCPエコシステム連携**: VSCode、GitHub Copilot、Claude Desktop等で利用可能

---

## 🛠 機能要件

### Core MCP Tools

| ツール名 | 入力 | 出力 | 役割 |
|---------|------|------|------|
| `reason_about_change` | user_intent, current_state, proposed_action | 自然言語の推論結果 | GSRに則った推論エンジン |
| `validate_against_constraints` | proposed_change, reasoning_context | ✅/❌/⚠️付き検証結果 | 制約適合性チェック |
| `execute_with_safeguards` | action_description, dry_run=True | 実行レポート | 安全な変更適用 |

### MCP Resources

| リソース名 | 内容 | 用途 |
|-----------|------|------|
| `read_constraints` | constraints.txtの内容 | 制約ルールの参照 |
| `read_reasoning_log` | 推論過程のログ | トレーサビリティ確保 |

---

## 🚫 非機能要件

### 安全性要件
- **stdout禁止**: MCPプロトコル保護のため、ログは`stderr`のみ
- **サンドボックス実行**: 全変更を`git worktree`で隔離
- **dry-run優先**: 実行前に必ず乾式実行で検証

### 性能要件
- **軽量性**: 依存関係最小化（Hydra/Kedro/MLflowは検証環境に分離）
- **応答性**: 推論結果は3秒以内で返却
- **スケーラビリティ**: 複数クライアント同時接続対応

### 保守性要件
- **DRY**: コード重複排除
- **KISS**: 過剰な抽象化回避
- **YAGNI**: 必要最小限の機能実装
- **SOLID**: 依存性逆転による疎結合設計

---

## 🔌 対応アプリケーション

| アプリ | 接続方式 | 設定ファイル |
|-------|----------|-------------|
| Claude Desktop | STDIO | claude_desktop_config.json |
| VSCode + GitHub Copilot | MCP Extension | workspace settings |
| Cursor | 組み込みMCP | .cursorrules |
| Kiro/Cline | CLI連携 | .clinerules |

---

## 📊 測定・検証要件

### 性能指標
- **SWE-Bench Lite正解率**: 目標62.3%以上
- **制約適合率**: 95%以上
- **安全実行成功率**: 99%以上

### 検証方法
- **MLflow**: 実験トラッキング（評価環境）
- **Prefect**: ワークフロー自動化
- **pytest**: 単体・統合テスト
- **README可視化**: 性能グラフの掲載

---

## 🏗 システム構成

```
CoreThink-MCP Production Server
├── src/corethink_mcp/server/     # 配布用MCPサーバー
├── src/corethink_mcp/constraints.txt  # 制約ルール
└── logs/                         # 推論ログ

Evaluation Environment (別管理)
├── src/evaluation/               # 検証用コード
├── conf/                         # Hydra設定
└── data/                         # SWE-Benchデータ
```

---

## 🔐 セキュリティ要件

### アクセス制御
- **ユーザー承認**: execute_with_safeguards実行時の明示的確認
- **権限分離**: 読み取り専用リソースと書き込み可能ツールの分離
- **監査ログ**: 全操作の自然言語による記録

### データ保護
- **機密情報除外**: パスワード・APIキーの検出・除外
- **差分制限**: 大容量ファイルの変更制限
- **履歴保護**: .gitによる変更履歴保護

---

## 🌐 多言語対応

### 初期実装
- **Python 3.11.12**: メインサーバー（uv管理）
- **STDIO通信**: 標準入出力によるMCP通信

### 将来拡張
- **Node.js版**: 純実装またはPythonラッパー
- **HTTP API**: REST APIによるクライアント連携

---

## 📝 ドキュメント要件

### 開発者向け
- **GitHub Copilot設定**: `.github/copilot-instructions.md`
- **IDE連携ルール**: `.cursorrules`, `.clinerules`
- **API仕様**: MCPツール・リソースの詳細

### ユーザー向け
- **クイックスタート**: 5分で動作確認可能な手順
- **使用例**: 実際のバグ修正シナリオ
- **トラブルシューティング**: よくある問題と解決策

---

## ✅ 受け入れ基準

### MVP完了条件
1. ✅ 3つのコアツールが動作
2. ✅ Claude Desktopから呼び出し可能
3. ✅ constraints.txtによる制約検証
4. ✅ サンドボックス環境での安全実行
5. ✅ 自然言語での推論結果出力

### 本格運用条件
1. ✅ SWE-Bench Lite での測定完了
2. ✅ MLflowによる性能記録
3. ✅ README.mdへのグラフ掲載
4. ✅ PyPIパッケージ公開
5. ✅ 複数IDE/エディタでの動作確認

---

## 🔄 運用要件

### デプロイメント
- **パッケージ配布**: PyPI/npm経由
- **コンテナ化**: Docker対応（オプション）
- **CI/CD**: GitHub Actionsによる自動テスト

### 監視・保守
- **エラー監視**: ログファイルによる異常検知
- **性能監視**: 応答時間・メモリ使用量の追跡
- **更新戦略**: 下位互換性を保った段階的アップデート

---

*このドキュメントは、CoreThink論文のGSR思想とMCPエコシステムの要求を統合し、実用的で安全なLLM拡張システムの仕様を定義しています。*
