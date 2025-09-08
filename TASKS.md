# 📄 CoreThink-MCP タスク一覧

このドキュメントでは、CoreThink-MCPプロジェクトの実装タスクを詳細に分類・管理します。

## ✅ 完了済みタスク

### 📁 プロジェクト基盤
- [x] pyproject.toml 作成（依存関係定義）
- [x] constraints.txt 制約ルール定義
- [x] .github/copilot-instructions.md GitHub Copilot設定
- [x] .cursorrules Cursor IDE設定
- [x] .clinerules Kiro/Cline設定
- [x] .env.example 環境変数テンプレート
- [x] docker-compose.yml コンテナ設定
- [x] 要件定義仕様書作成
- [x] 実装計画書作成

## 🔄 進行中タスク

### 🛠 MCP サーバー実装
- [ ] src/corethink_mcp/server/corethink_server.py メインサーバー
- [ ] src/corethink_mcp/server/utils.py ユーティリティ関数
- [ ] src/corethink_mcp/server/__init__.py パッケージ初期化

### 🔧 コアツール実装
- [ ] reason_about_change ツール（GSR推論エンジン）
- [ ] validate_against_constraints ツール（制約検証）
- [ ] execute_with_safeguards ツール（安全実行）

### 📚 MCP リソース実装
- [ ] read_constraints リソース（制約参照）
- [ ] read_reasoning_log リソース（ログ参照）

## � 緊急対応項目

### Claude系MCPエコシステム対応 🔥

| 項目 | 説明 | 優先度 | 状況 |
|------|------|---------|------|
| Remote MCP対応 | claude.ai Connectorsでの利用を可能にする | 🔥 緊急 | ✅ 完了 |
| HTTP Transport実装 | aiohttp使用のRemote MCPサーバー | 🔥 緊急 | ✅ 完了 |
| 自動セットアップツール | 設定ファイル生成の自動化 | 🔥 緊急 | ✅ 完了 |
| セキュリティ準拠 | Anthropic公式ガイドラインへの対応 | 🔥 緊急 | 🔄 進行中 |
| OAuth認証システム | Remote MCP用認証機能 | 📋 重要 | 📅 計画中 |
| VS Code ギャラリー登録 | 公式ディレクトリへの申請 | 📋 重要 | 📅 計画中 |

### 実装済み改善点 ✅

- **Remote MCP Server**: HTTP Transport対応、CORS設定済み
- **Setup Helper Tool**: 自動設定ファイル生成、Claude Desktop自動インストール
- **Docker Multi-Service**: Local/Remote MCP両対応
- **aiohttp依存関係追加**: pyproject.tomlに追加済み
- **🆕 .DXT Package対応**: Claude Desktopのドラッグ&ドロップインストール対応

### 🚀 新機能: .DXT Package ✅

| 項目 | 説明 | 状況 |
|------|------|------|
| .DXT Package作成 | Claude Desktop用ドラッグ&ドロップファイル | ✅ 完了 |
| DXT仕様準拠 | Anthropic公式DXT仕様v0.0.1に準拠 | ✅ 完了 |
| マニフェスト設計 | tools, resources, user_config完備 | ✅ 完了 |
| Setup Helper統合 | `python setup_helper.py dxt`で生成可能 | ✅ 完了 |

**使用方法**:
```bash
# .DXTファイル生成
python setup_helper.py dxt
# Claude Desktop > 拡張機能 > corethink-mcp.dxt をドラッグ&ドロップ
```

## �📋 継続中のタスク

### 🏗 環境構築
- [x] UV仮想環境作成
- [x] 依存関係インストール確認
- [ ] ログディレクトリ設定
- [ ] Git worktree テスト環境構築

### 🔌 IDE連携テスト
- [ ] Claude Desktop 接続テスト
- [ ] VSCode + GitHub Copilot 連携確認
- [ ] Cursor 動作確認
- [ ] Kiro/Cline 動作確認

### 🚀 配布・拡張
- [ ] **VS Code MCP ギャラリーへの登録** 🆕
  - VS Code 1.102+ の正式MCPサポートに対応
  - MCP Servers ギャラリーでの検索・インストール対応
  - プロファイル・Settings Sync対応
- [ ] PyPI パッケージ公開
- [ ] NPM パッケージ公開（Node.js版）
- [ ] Docker Hub イメージ公開

### 🌍 多言語対応 🆕
- [ ] **英語版README作成** (`README_EN.md`)
  - 国際的なユーザーベース拡大
  - GitHubでの検索・発見性向上
  - CoreThink論文の正確な英語説明
- [ ] **中国語版README作成** (`README_CN.md`)
  - 中国語圏のデベロッパー対応
  - 技術文書の中国語ローカライゼーション
  - 簡体字・繁体字両対応検討

### 🔧 システム改善 🆕
- [ ] **ポート自動変更機能**
  - ポート8080競合時の自動ポート検出
  - 利用可能ポートの自動選択機能
  - ポート変更時のログ出力・通知

### 🧪 テスト実装
- [ ] 単体テスト作成（pytest）
- [ ] 統合テスト作成
- [ ] MCP プロトコルテスト
- [ ] エラーハンドリングテスト

### 📊 検証環境構築
- [ ] src/evaluation/ ディレクトリ作成
- [ ] MLflow 実験トラッキング設定
- [ ] Prefect ワークフロー構築
- [ ] SWE-Bench Lite データ準備

### 📖 ドキュメント作成
- [ ] README.md 詳細版作成
- [ ] API 仕様書作成
- [ ] ユーザーガイド作成
- [ ] トラブルシューティングガイド

### 🚀 配布準備
- [ ] PyPI パッケージ設定
- [ ] CI/CD パイプライン構築
- [ ] Node.js 版サーバー設計
- [ ] Docker コンテナ最適化

## 🎯 今すぐ実行すべきタスク

### Phase 1: 基本環境構築（今週）
1. **UV環境構築**
   ```bash
   uv venv --python 3.11.12
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv add mcp[cli] fastmcp pyyaml gitpython python-dotenv
   ```

2. **メインサーバーファイル作成**
   - `src/corethink_mcp/server/corethink_server.py`
   - FastMCP ベースのサーバー骨格
   - 3つのコアツール実装

3. **基本動作確認**
   - サーバー起動テスト
   - MCP プロトコル応答確認
   - Claude Desktop 接続テスト

### Phase 2: 機能実装（来週）
1. **GSR推論エンジン実装**
   - reason_about_change の自然言語推論ロジック
   - constraints.txt 参照機能
   - PROCEED/CAUTION/REJECT 判定

2. **制約検証機能実装**
   - validate_against_constraints の制約チェック
   - 違反検出・報告機能
   - 自然言語による説明生成

3. **安全実行機能実装**
   - execute_with_safeguards のサンドボックス実行
   - git worktree による隔離
   - dry-run 機能

## ⚠️ ブロッカー・リスク

### 技術的課題
- [ ] FastMCP の最新仕様確認
- [ ] MCP クライアント（Claude Desktop等）の設定方法調査
- [ ] GitPython での worktree 操作実装方法

### 依存関係
- [ ] Python 3.11.12 の動作確認
- [ ] uv パッケージマネージャーの安定性
- [ ] MCPエコシステムの成熟度

### スケジュール
- [ ] 実装時間の見積もり精緻化
- [ ] 検証環境構築の工数
- [ ] 複数IDE対応のテスト時間

## 📈 進捗管理

### 完了率
- プロジェクト基盤: 90% ✅
- 環境設定: 80% ✅
- コア実装: 10% 🔄
- テスト: 0% ⏳
- ドキュメント: 60% ✅
- 配布準備: 0% ⏳

### 今週の目標
- [x] 要件定義・実装計画完成
- [ ] UV環境構築完了
- [ ] メインサーバーファイル作成
- [ ] 1つ目のツール動作確認

### 来週の目標
- [ ] 3つのコアツール完成
- [ ] Claude Desktop 連携成功
- [ ] 基本的な制約検証動作
- [ ] サンドボックス実行確認

---

*このタスク一覧は、CoreThink-MCPの開発進捗を追跡し、効率的な実装を支援するために作成されています。定期的に更新し、プロジェクトの成功を確実にします。*
