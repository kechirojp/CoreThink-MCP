# 🧠 CoreThink-MCP

**A General Symbolics Reasoning (GSR) powered MCP Server for safe, natural language reasoning in code changes**

CoreThink-MCP は、[CoreThink論文](https://arxiv.org/abs/2509.00971)で提案された **General Symbolics Reasoning (GSR)** の思想を実装した Model Context Protocol (MCP) サーバーです。LLMが自然言語のまま推論・制約検証・安全実行を行える「外付け推論レイヤー」として機能します。

## 🎯 特徴

- **🔍 自然言語内推論**: JSON構造化せず、言語のまま推論過程を保持
- **🛡️ 制約駆動検証**: constraints.txtによるルールベース安全性チェック  
- **⚡ サンドボックス実行**: git worktreeによる隔離された安全な変更適用
- **🔌 広範囲対応**: Claude Desktop、VSCode、Cursor、Kiro、Clineで利用可能
- **🔄 段階的実行**: dry-run → 検証 → 適用の安全な流れ

## 🚀 クイックスタート

### 1. インストール

```bash
# リポジトリをクローン
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP

# UV環境構築
uv venv --python 3.11.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係インストール
uv add mcp[cli] fastmcp pyyaml gitpython python-dotenv
```

### 2. サーバー起動

```bash
# 開発モード
python src/corethink_mcp/server/corethink_server.py

# または UV環境
uv run python src/corethink_mcp/server/corethink_server.py

# または Docker
docker-compose up
```

### 3. MCP接続設定

**詳細なセットアップ手順は [SETUP.md](SETUP.md) を参照してください。**

#### Claude Desktop

基本設定例（`claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "python",
      "args": ["src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/absolute/path/to/your/CoreThink-MCP"
    }
  }
}
```

#### VS Code (v1.102以降) 🆕

**MCPサポートが正式版になりました！** VS Code 1.102以降では、以下の方法でMCPサーバーを簡単にインストール・管理できます：

**方法1: MCP Servers ギャラリー（推奨）**
1. VS Codeで `Ctrl+Shift+X` を押して拡張機能ビューを開く
2. **MCP SERVERS** セクションを探す
3. **Browse MCP Servers...** をクリック
4. [VS Code MCP ギャラリー](https://code.visualstudio.com/mcp) から検索・インストール

**方法2: 手動設定**
1. `Ctrl+Shift+P` でコマンドパレットを開く
2. **MCP: Open User Configuration** を実行
3. `mcp.json` ファイルに以下を追加：

```json
{
  "servers": {
    "corethink-mcp": {
      "command": "python",
      "args": ["src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/absolute/path/to/your/CoreThink-MCP"
    }
  }
}
```

**新機能（VS Code 1.102+）:**
- ✅ **MCP Servers管理ビュー**: Extensions ビューで一元管理
- ✅ **プロファイル対応**: 各プロファイルごとに異なるMCPサーバー設定
- ✅ **Settings Sync**: MCPサーバー設定の同期対応
- ✅ **Dev Container対応**: `devcontainer.json` での設定可能
- ✅ **リアルタイム管理**: Start/Stop/Restart、ログ表示、設定確認

#### LM Studio (v0.3.17以降) 🆕

**ローカルLLMとMCPの強力な組み合わせ！**

**🚀 ワンクリックインストール:**

[![Add CoreThink-MCP to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInB5dGhvbiIsICJhcmdzIjogWyJzcmMvY29yZXRoaW5rX21jcC9zZXJ2ZXIvY29yZXRoaW5rX3NlcnZlci5weSJdLCAiY3dkIjogIi9hYnNvbHV0ZS9wYXRoL3RvL3lvdXIvQ29yZVRoaW5rLU1DUCJ9fQ==)

**UV環境使用の場合:**

[![Add CoreThink-MCP (UV) to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp-uv&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInV2IiwgImFyZ3MiOiBbInJ1biIsICJweXRob24iLCAic3JjL2NvcmV0aGlua19tY3Avc2VydmVyL2NvcmV0aGlua19zZXJ2ZXIucHkiXSwgImN3ZCI6ICIvYWJzb2x1dGUvcGF0aC90by95b3VyL0NvcmVUaGluay1NQ1AifX0=)

**⚠️ 重要**: インストール後、`cwd` のパスを必ずあなたの環境に合わせて変更してください。

**手動設定方法:**
1. LM Studio で **Program** タブを開く
2. **Install > Edit mcp.json** をクリック
3. 以下の設定を追加：

```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "python",
      "args": ["src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/absolute/path/to/your/CoreThink-MCP"
    }
  }
}
```

**特徴:**
- 🖥️ **完全ローカル**: インターネット不要でプライベート推論
- ⚡ **高速処理**: ローカルLLMとMCPの直接統合
- 🛡️ **セキュリティ**: データが外部に送信されない
- 🔧 **カスタマイズ**: LLMモデルの自由選択

**⚠️ 重要**: `cwd` のパスは必ずあなたの環境に合わせて変更してください。

## 🛠 利用可能なツール

| ツール | 説明 | 出力例 |
|-------|------|--------|
| `reason_about_change` | GSR推論エンジン | 【判定】PROCEED_WITH_CAUTION, 【理由】制約に適合, 【次ステップ】詳細検証 |
| `validate_against_constraints` | 制約適合性検証 | ✅ MUST適合 ❌ NEVER違反, ⚠️ SHOULD推奨 |
| `execute_with_safeguards` | 安全な変更実行 | 【DRY RUN】サンドボックスで実行, 実ファイルに影響なし |

## 📚 リソース

- **constraints**: 制約ルールファイルの内容
- **reasoning_log**: 推論過程のトレースログ

## 🛠 使用方法

### 基本的な使用例

1. **推論開始**
   ```
   ユーザー: "calc.pyのゼロ除算バグを直して"
   ```

2. **システムが自動で推論**
   - `reason_about_change` で意図分析
   - `validate_against_constraints` で制約確認
   - `execute_with_safeguards` で安全実行

3. **自然言語での結果**
   ```
   【判定】PROCEED
   【理由】すべての制約に適合
   【次ステップ】パッチ生成 → 検証 → 適用
   ```

## 📁 プロジェクト構造

```
corethink-mcp/
├── src/corethink_mcp/          # メインパッケージ
│   ├── server/                 # MCPサーバー
│   │   ├── corethink_server.py # メインサーバー
│   │   └── utils.py           # ユーティリティ
│   └── constraints.txt        # 制約ルール
├── conf/base/                 # 設定ファイル
├── logs/                      # ログ出力
├── .github/                   # GitHub設定
│   └── copilot-instructions.md # Copilot向けルール
├── pyproject.toml             # プロジェクト設定
└── docker-compose.yml         # Docker設定
```

## 🔧 設定

### 環境変数 (.env)

```bash
CORETHINK_REPO_ROOT=.              # 対象リポジトリ
CORETHINK_LOG_LEVEL=INFO           # ログレベル
CORETHINK_PORT=8080                # サーバーポート
CORETHINK_SANDBOX_DIR=.sandbox     # サンドボックス名
```

### 制約ファイル (constraints.txt)

```
MUST: 公開APIの変更を禁止
NEVER: printやconsole.logなどのデバッグ出力を追加しない
SHOULD: 関数変更時はdocstringを更新する
MUST: すべてのテストがパスすること
```

```bash
CORETHINK_REPO_ROOT=.              # 対象リポジトリ
CORETHINK_LOG_LEVEL=INFO           # ログレベル
CORETHINK_PORT=8080                # サーバーポート
CORETHINK_SANDBOX_DIR=.sandbox     # サンドボックス名
```

### 制約ファイル (constraints.txt)

```
MUST: 公開APIの変更を禁止
NEVER: printやconsole.logなどのデバッグ出力を追加しない
SHOULD: 関数変更時はdocstringを更新する
MUST: すべてのテストがパスすること
```

## 🧪 開発・ロードマップ

### 設計原則

- **DRY**: 重複コードの排除
- **KISS**: シンプルな構造
- **YAGNI**: 必要最小限の機能
- **SOLID**: 依存性の管理

### ロードマップ

- [x] Phase 1: MVP（基本3ツール）
- [ ] Phase 2: 高度な制約学習
- [ ] Phase 3: Node.js版サーバー
- [ ] Phase 4: MLflow連携での性能測定
- [ ] Phase 5: PyPI公開

## 🤝 対応アプリケーション

- ✅ **VS Code (v1.102以降)** - MCPサポート正式版、管理ビュー対応 🆕
- ✅ **LM Studio (v0.3.17以降)** - ローカルLLM + MCP統合対応 🆕
- ✅ **Claude Desktop** - フル機能対応
- ✅ **Cursor** - MCP統合対応
- ✅ **Kiro** - コード生成・編集対応
- ✅ **Cline** - AI開発アシスタント対応

## 📊 性能・検証

- **SWE-Bench Lite**: 目標正解率62.3%以上
- **制約適合率**: 95%以上
- **安全実行成功率**: 99%以上

性能測定結果は [MLflow](https://mlflow.org/) で追跡し、随時更新されます。

## � CoreThink論文への謝辞

本プロジェクトは、以下の研究成果にインスパイアされています：

**"CoreThink: A Symbolic Reasoning Layer to reason over Long Horizon Tasks with LLMs"**  
*Jay Vaghasiya, Omkar Ghugarkar, Vishvesh Bhat, Vipul Dholaria, Julian McAuley*  
arXiv:2509.00971v2 [cs.AI] 4 Sep 2025

CoreThink論文で提案された **General Symbolics Reasoning (GSR)** フレームワークの実装により、LLMの「チェーン・オブ・ソート（CoT）」の限界を克服し、自然言語内での正確で透明な推論を実現しています。

## 📄 ライセンス

このプロジェクトは **MIT License** の下で公開されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。

### オープンソース利用について

- ✅ **商用利用可**: 企業での利用・改変・配布可能
- ✅ **改変・再配布可**: ソースコード改変・再配布可能  
- ✅ **プライベート利用可**: 非公開プロジェクトでの利用可能
- ⚠️ **MIT License表示**: ライセンス表示の保持が必要
- ⚠️ **免責事項**: 作者は一切の保証・責任を負いません

## 🤝 コントリビューション

コントリビューションを歓迎します！以下のガイドラインに従ってください：

1. **Issue** で提案・バグ報告
2. **Fork** してフィーチャーブランチ作成
3. **Pull Request** で変更をマージ
4. **GSR思想** と **DRY/KISS/YAGNI/SOLID** 原則の遵守

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## 🔗 関連リンク

- **論文**: [CoreThink: A Symbolic Reasoning Layer](https://arxiv.org/abs/2509.00971)
- **MCP公式**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **FastMCP**: [FastMCP Framework](https://gofastmcp.com/)
- **プロジェクトドキュメント**: [詳細ドキュメント](./docs/)

## 🏷️ タグ

`#MCP` `#ModelContextProtocol` `#GSR` `#GeneralSymbolics` `#CoreThink` `#NaturalLanguageReasoning` `#SafeLLM` `#GitHubCopilot` `#ClaudeDesktop` `#VSCode` `#Python` `#FastMCP`

## 📞 サポート

Issue やプルリクエストをお待ちしています！

[GitHub Issues](https://github.com/kechirojp/CoreThink-MCP/issues)

---

*このプロジェクトは、LLMエコシステムに安全で高性能な推論レイヤーを提供し、AIとの協働をより透明で信頼できるものにすることを目指しています。*
