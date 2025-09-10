# CoreThink-MCP 要件定義仕様書（最終更新：2025年9月11日）

## 📄 プロジェクト概要

### 🎯 目的
**CoreThink論文（arXiv:2509.00971v2）のGeneral Symbolics Reasoning（GSR）**を実装した Model Context Protocol（MCP）サーバーを構築し、あらゆるLLMの推論能力を向上させる実用的システムを提供する。

### 🔑 核心価値
- **自然言語内直接推論**: symbolic-neural間の変換損失を回避し、NL-to-NLで一貫した推論
- **安全な段階的実行**: git worktreeサンドボックス環境での隔離実行とdry-run機能
- **制約駆動検証**: constraints.txtによる厳密なルールベース検証システム
- **ユニバーサル対応**: Claude Desktop、VS Code、LM Studio等、あらゆるMCP対応アプリで利用可能
- **Python-first戦略**: メインデプロイメントはPython、将来連携のための技術的拡張性保持
- **Elicitation機能**: ユーザー入力要求による動的情報収集

---

## 🛠 機能要件

### 実装済みコア機能 ✅

#### Core MCP Tools（動作確認済み）

| ツール名 | 入力 | 出力 | 役割 | 実装状況 |
|---------|------|------|------|----------|
| `reason_about_change` | user_intent, context | GSR推論による判定結果 | CoreThink GSR推論エンジン | ✅ 実装完了 |
| `validate_against_constraints` | proposed_change, context | 制約適合性評価 | constraints.txt検証 | ✅ 実装完了 |
| `execute_with_safeguards` | action, dry_run=True | 安全実行レポート | サンドボックス実行 | ✅ 実装完了 |
| `trace_reasoning_steps` | user_query, context | 推論過程トレース | 透明性・検証可能性 | ✅ 実装完了 |
| `refine_understanding` | ambiguous_input, context | 曖昧性解消結果 | 語義曖昧性解消 | ✅ 実装完了 |
| `orchestrate_multi_step_reasoning` | task, subtasks | 複数段階推論統制 | 階層的タスク分解 | ✅ 実装完了 |
| `learn_dynamic_constraints` | examples, violations | 動的制約学習 | 自動制約生成 | ✅ 実装完了 |
| `detect_symbolic_patterns` | input_data, pattern_type | パターン検出結果 | ARC-AGI-2準拠検出 | ✅ 実装完了 |
| `analyze_repository_context` | repo_path, scope | リポジトリ分析結果 | SWE-Bench技術活用 | ✅ 実装完了 |

#### Elicitation機能（ユーザー入力要求）✅

| コンポーネント | 機能 | 実装状況 |
|---------------|------|----------|
| `elicitation.py` | 基本Elicitation機能 | ✅ 実装完了 |
| `elicitation_client.py` | クライアント実装 | ✅ 実装完了 |
| `elicitation_server.py` | サーバー実装 | ✅ 実装完了 |
| `test_elicitation.py` | テストファイル | ✅ 実装完了 |

#### MCP Resources（提供中）

| リソース名 | 内容 | 用途 | 実装状況 |
|-----------|------|------|----------|
| `constraints` | constraints.txtの内容 | 制約ルール参照 | ✅ 実装完了 |
| `reasoning_log` | 推論過程のログ | トレーサビリティ | ✅ 実装完了 |

#### 配布・インストール方式

| 方式 | 対象アプリ | 実装状況 | 特徴 |
|------|-----------|----------|------|
| Python-first | 全アプリ | ✅ 実装完了 | メインデプロイメント戦略 |
| 手動インストール | VS Code | ✅ 実装完了 | ステップバイステップガイド |
| 自動同期システム | 連携機能 | ✅ 実装完了 | Python→Node.js自動同期 |
| 文字化け対策 | 全MCPクライアント | ✅ 実装完了 | PYTHONIOENCODING統一 |

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

## 🔌 対応アプリケーション（実装済み）

| アプリ | 接続方式 | 設定ファイル | インストール方法 | 実装状況 |
|-------|----------|-------------|-----------------|----------|
| Claude Desktop | STDIO/Local MCP | .dxt/.json | .DXTドラッグ&ドロップ | ✅ 完了 |
| claude.ai web | HTTP/Remote MCP | Connectors | カスタムConnector追加 | ✅ 完了 |
| VS Code 1.102+ | MCP Extension | mcp.json | MCP Serversギャラリー | 📅 ギャラリー登録予定 |
| LM Studio 0.3.17+ | Local MCP | mcp.json | ワンクリック/deeplink | ✅ 完了 |
| Cursor | 組み込みMCP | .cursorrules | 手動設定 | ✅ 完了 |

### バージョン管理・自動化機能

| 機能 | 実装状況 | 説明 |
|------|----------|------|
| セマンティックバージョニング | ✅ v1.0.0 | pyproject.toml、__init__.py、サーバーで統一 |
| ポート自動検出 | ✅ 完了 | 8080競合時の自動ポート変更 |
| 環境変数管理 | ✅ 完了 | .env.example テンプレート提供 |
| Docker対応 | ✅ 完了 | Local/Remote MCP両対応 |
| Setup Helper | ✅ 完了 | 自動設定ファイル生成・インストール |

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

### ✅ 実装完了
- **Python 3.11.12**: メインサーバー（uv管理）
- **STDIO通信**: 標準入出力によるMCP通信
- **Node.js/TypeScript版**: ハイブリッドアーキテクチャ実装完了
  - Node.js フロントエンド + Python GSR エンジン
  - @modelcontextprotocol/sdk v1.0.0 対応
  - npm パッケージ配布準備完了
  - VS Code ワンクリックインストール対応

### 将来拡張
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

## ✅ 受け入れ基準（現在の達成状況）

### MVP完了条件 ✅ 達成済み

1. ✅ **3つのコアツール動作確認済み**
   - reason_about_change: GSR推論による自然言語判定
   - validate_against_constraints: 制約適合性検証
   - execute_with_safeguards: サンドボックス安全実行

2. ✅ **マルチアプリ対応完了**
   - Claude Desktop: .DXTドラッグ&ドロップインストール
   - claude.ai web: Remote MCP HTTP Transport
   - VS Code: MCP Extension設定
   - LM Studio: ワンクリックdeeplink

3. ✅ **安全性機能実装完了**
   - constraints.txt制約検証システム
   - git worktreeサンドボックス環境
   - dry-run機能によるリスク軽減

4. ✅ **自然言語出力システム**
   - JSON構造化せず、言語のまま推論結果出力
   - PROCEED/CAUTION/REJECT判定システム
   - 推論過程の透明性確保

### 本格運用準備

| 項目 | 現在の状況 | 次ステップ |
|------|------------|-----------|
| パフォーマンス測定 | 📅 計画中 | SWE-Bench Lite テスト実行 |
| PyPI公開 | 📅 準備中 | パッケージング最終調整 |
| VS Code Gallery登録 | 📅 申請予定 | MCP Servers Gallery申請 |
| 多言語ドキュメント | 📅 計画中 | 英語・中国語README作成 |
| 企業向け機能 | 📅 検討中 | OAuth認証、監査ログ強化 |

---

## 🔄 運用要件

### デプロイメント
- **パッケージ配布**: 
  - ✅ **Python**: PyPI準備完了
  - ✅ **Node.js**: npm パッケージ実装完了（@corethink/mcp）
- **コンテナ化**: Docker対応（オプション）
- **CI/CD**: GitHub Actionsによる自動テスト

### 監視・保守
- **エラー監視**: ログファイルによる異常検知
- **性能監視**: 応答時間・メモリ使用量の追跡
- **更新戦略**: 下位互換性を保った段階的アップデート

---

*このドキュメントは、CoreThink論文のGSR思想とMCPエコシステムの要求を統合し、実用的で安全なLLM拡張システムの仕様を定義しています。*
