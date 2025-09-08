# 🧠 CoreThink-MCP

**A General Symbolics Reasoning (GSR) powered MCP Server for safe, natural language reasoning in code changes**

CoreThink-MCP は、[CoreThink論文](https://arxiv.org/abs/2509.00971)で提案された **General Symbolics Reasoning (GSR)** の思想を実装した Model Context Protocol (MCP) サーバーです。LLMが自然言語のまま推論・制約検証・安全実行を行える「外付け推論レイヤー」として機能します。

## 🎯 特徴

- **🔍 自然言語内推論**: JSON構造化せず、言語のまま推論過程を保持
- **🛡️ 制約駆動検証**: constraints.txtによるルールベース安全性チェック  
- **⚡ サンドボックス実行**: git worktreeによる隔離された安全な変更適用
- **🔌 広範囲対応**: Claude Desktop、VSCode、Cursor、Kiro、Clineで利用可能

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
python src/corethink_mcp/server/corethink_server.py
```

### 3. Claude Desktopで使用

**詳細なセットアップ手順は [SETUP.md](SETUP.md) を参照してください。**

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

**⚠️ 重要**: `cwd` のパスは必ずあなたの環境に合わせて変更してください。

**重要**: `cwd` フィールドは必ずあなたの環境でのCoreThink-MCPプロジェクトの**絶対パス**に変更してください。

### UV使用の場合

UV環境を使用する場合は、以下の設定を使用してください：

```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "uv",
      "args": ["run", "python", "src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/absolute/path/to/your/CoreThink-MCP"
    }
  }
}
```

## 🛠 利用可能なツール

| ツール | 説明 | 出力例 |
|-------|------|--------|
| `reason_about_change` | GSR推論エンジン | 【判定】PROCEED_WITH_CAUTION<br>【理由】制約に適合<br>【次ステップ】詳細検証 |
| `validate_against_constraints` | 制約適合性検証 | ✅ MUST適合 ❌ NEVER違反<br>⚠️ SHOULD推奨 |
| `execute_with_safeguards` | 安全な変更実行 | 【DRY RUN】サンドボックスで実行<br>実ファイルに影響なし |

## 📚 リソース

- **constraints**: 制約ルールファイルの内容
- **reasoning_log**: 推論過程のトレースログ

## 🔬 CoreThink論文への謝辞

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

## 📊 性能・検証

- **SWE-Bench Lite**: 目標正解率62.3%以上
- **制約適合率**: 95%以上
- **安全実行成功率**: 99%以上

性能測定結果は [MLflow](https://mlflow.org/) で追跡し、随時更新されます。

## 🔗 関連リンク

- **論文**: [CoreThink: A Symbolic Reasoning Layer](https://arxiv.org/abs/2509.00971)
- **MCP公式**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **FastMCP**: [FastMCP Framework](https://gofastmcp.com/)
- **ドキュメント**: [プロジェクトドキュメント](./docs/)

## 🏷️ タグ

`#MCP` `#ModelContextProtocol` `#GSR` `#GeneralSymbolics` `#CoreThink` `#NaturalLanguageReasoning` `#SafeLLM` `#GitHubCopilot` `#ClaudeDesktop` `#VSCode` `#Python` `#FastMCP`

---

*このプロジェクトは、LLMエコシステムに安全で高性能な推論レイヤーを提供し、AIとの協働をより透明で信頼できるものにすることを目指しています。*

**GSR（General Symbolics Reasoning）に基づく自然言語推論MCPサーバー**

## 🎯 概要

CoreThink-MCPは、論文「CoreThink: A Symbolic Reasoning Layer to reason over Long Horizon Tasks with LLMs」で提案されたGSRフレームワークを、Model Context Protocol（MCP）サーバーとして実装したものです。

既存のLLM（Claude, GPT, etc.）に「推論の制約・検証・修正・実行」を可能にする「外付けの賢いアシスタント」として機能します。

## ✨ 特徴

- 🔍 **自然言語内推論**: JSONや構造化データではなく、自然言語のまま推論
- 🔒 **サンドボックス実行**: Git worktreeによる安全な隔離環境
- 📋 **制約検証**: constraints.txtによる自動的な安全性チェック
- 🔄 **段階的実行**: dry-run → 検証 → 適用の安全な流れ
- 🛠 **MCP対応**: VSCode, Claude Desktop, Cursor等と連携

## 🚀 クイックスタート

### 1. 環境構築

```bash
# Python 3.11.12 + UV環境
uv venv --python 3.11.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係インストール
uv add mcp[cli] fastmcp PyYAML GitPython python-dotenv
```

### 2. サーバー起動

```bash
# 開発モード
uv run src/corethink_mcp/server/corethink_server.py

# または Docker
docker-compose up
```

### 3. MCP接続設定

#### Claude Desktop
`claude_desktop_config.json` に追加:
```json
{
  "mcpServers": {
    "corethink": {
      "command": "uv",
      "args": ["run", "src/corethink_mcp/server/corethink_server.py"]
    }
  }
}
```

#### VSCode + GitHub Copilot
1. MCP Extensionをインストール
2. 設定でサーバーを追加

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

### 利用可能なツール

| ツール | 機能 | 出力 |
|--------|------|------|
| `reason_about_change` | GSR推論エンジン | 推論過程+判定 |
| `validate_against_constraints` | 制約検証 | ✅/❌/⚠️ 付き結果 |
| `execute_with_safeguards` | 安全実行 | 実行結果+影響範囲 |

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

## 🧪 開発

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

- ✅ VSCode + GitHub Copilot
- ✅ Claude Desktop
- ✅ Cursor
- ✅ Kiro
- ✅ Cline

## 📊 性能

*（MLflow連携での測定結果を今後掲載予定）*

## 📝 ライセンス

[ライセンス情報を追加]

## 🙏 謝辞

論文「CoreThink: A Symbolic Reasoning Layer to reason over Long Horizon Tasks with LLMs」の著者に感謝します。

---

## 🔗 関連リンク

- [Model Context Protocol 公式ドキュメント](https://modelcontextprotocol.io/)
- [CoreThink 論文](https://example.com/corethink-paper)

## 📞 サポート

Issue やプルリクエストをお待ちしています！
