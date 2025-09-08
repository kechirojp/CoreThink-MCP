# 🧠 CoreThink-MCP

**A General Symbolics Reasoning (GSR) powered MCP Server for safe, natural language reasoning in code changes**

CoreThink-MCP は、[CoreThink論文](https://arxiv.org/abs/2509.00971)で提案された **General Symbolics Reasoning (GSR)** の思想を実装した Model Context Protocol (MCP) サーバーです。LLMが自然言語のまま推論・制約検証・安全実行を行える「外付け推論レイヤー」として機能します。

## 📋 目次

- [🎯 特徴](#-特徴)
- [🚀 クイックスタート](#-クイックスタート)
- [📱 アプリケーション設定](#-アプリケーション設定)
- [🛠 利用可能なツール](#-利用可能なツール)
- [⚙️ 高度な設定](#️-高度な設定)
- [🔧 トラブルシューティング](#-トラブルシューティング)
- [📁 プロジェクト構造](#-プロジェクト構造)
- [🧪 開発・ロードマップ](#-開発ロードマップ)
- [🤝 対応アプリケーション](#-対応アプリケーション)

## 🎯 特徴

- **🔍 自然言語内推論**: JSON構造化せず、言語のまま推論過程を保持
- **🛡️ 制約駆動検証**: constraints.txtによるルールベース安全性チェック  
- **⚡ サンドボックス実行**: git worktreeによる隔離された安全な変更適用
- **🔌 広範囲対応**: Claude Desktop、VSCode、Cursor、Kiro、Clineで利用可能
- **🔄 段階的実行**: dry-run → 検証 → 適用の安全な流れ

## 🚀 クイックスタート

### 1. インストール

#### 🚀 UV環境での推奨インストール

UVは最新のPython依存関係管理ツールで、高速で安全な環境構築が可能です。

```bash
# リポジトリをクローン
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP

# UV環境構築（Python 3.11.12指定）
uv venv --python 3.11.12
# Windows
.venv\Scripts\activate
# macOS/Linux  
source .venv/bin/activate

# 依存関係インストール（UV推奨）
uv add mcp[cli] fastmcp pyyaml gitpython python-dotenv

# または requirements.txt 使用の場合
uv pip install -r requirements.txt
```

#### 🐍 標準Python環境

```bash
# リポジトリをクローン
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP

# 仮想環境作成
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 依存関係インストール
pip install mcp[cli] fastmcp pyyaml gitpython python-dotenv
```

**💡 UV環境の利点:**
- ⚡ **高速インストール**: pip比で10-100x高速
- 🔒 **一貫性保証**: `uv.lock`によるバージョン固定
- 🧹 **クリーンな依存関係**: 不要パッケージの自動除外
- 🔄 **高速リビルド**: キャッシュによる差分インストール

### 2. サーバー起動

#### UV環境での起動（推奨）

```bash
# 仮想環境アクティベート
# Windows
.venv\Scripts\activate
# macOS/Linux  
source .venv/bin/activate

# UV環境でサーバー起動
uv run python src/corethink_mcp/server/corethink_server.py

# または開発モードで起動
uv run --dev python src/corethink_mcp/server/corethink_server.py
```

#### 標準Python環境での起動

```bash
# 仮想環境アクティベート
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# サーバー起動
python src/corethink_mcp/server/corethink_server.py
```

#### Docker起動

```bash
# Docker Compose使用
docker-compose up

# 単体Docker起動
docker build -t corethink-mcp .
docker run -p 8080:8080 corethink-mcp
```

### 3. MCP接続設定

## 📱 アプリケーション設定

<details>
<summary>🎭 Claude Desktop 設定</summary>

### 設定ファイルの場所

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

### UV環境の場合（推奨）

```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "uv",
      "args": ["run", "python", "src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP"
    }
  }
}
```

### 標準Python環境の場合

```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "python",
      "args": ["src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP",
      "env": {
        "PATH": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP/.venv/bin:/YOUR_ABSOLUTE_PATH/CoreThink-MCP/.venv/Scripts:${PATH}"
      }
    }
  }
}
```

### パス設定の重要事項

**⚠️ 重要**: 必ず以下の点を確認してください：

1. `cwd` フィールドには、CoreThink-MCPプロジェクトの**絶対パス**を指定
2. パスの区切り文字は OS に応じて調整:
   - **Windows**: `C:\\Users\\YourName\\CoreThink-MCP`
   - **macOS/Linux**: `/home/yourname/CoreThink-MCP`
3. 仮想環境を使用する場合は、`env.PATH` を適切に設定

</details>

<details>
<summary>💻 VS Code (v1.102以降) 設定</summary>

**🎉 MCPサポートが正式版になりました！** VS Code 1.102以降では、MCPサーバーを公式サポートしており、以下の方法で簡単にインストール・管理できます：

### 推奨方法: MCP Servers ギャラリー 🆕

VS Code 1.102以降では、MCP Serversの管理が大幅に簡単になりました：

1. **拡張機能ビューを開く**: `Ctrl+Shift+X` (Windows/Linux) または `Cmd+Shift+X` (macOS)
2. **MCP SERVERS** セクションを探す
3. **Browse MCP Servers...** をクリック
4. [VS Code MCP ギャラリー](https://code.visualstudio.com/mcp) でCoreThink-MCPを検索
5. **Install** ボタンをクリックして自動インストール

> **📝 注意**: 現在ギャラリーへの登録を準備中です。登録完了まで手動設定をご利用ください。

### 手動設定方法

#### 設定ファイルアクセス
```bash
# ユーザー設定ファイルを開く
Ctrl+Shift+P → "MCP: Open User Configuration"

# リモート環境の場合
Ctrl+Shift+P → "MCP: Open Remote User Configuration"
```

#### UV環境使用の場合（推奨）
```json
{
  "servers": {
    "corethink-mcp": {
      "command": "uv",
      "args": ["run", "python", "src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP"
    }
  }
}
```

#### 標準Python環境使用の場合
```json
{
  "servers": {
    "corethink-mcp": {
      "command": "python",
      "args": ["src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP"
    }
  }
}
```

### 新機能 (VS Code 1.102+)

#### MCP Servers 管理ビュー
- **Extensions ビュー** → **MCP SERVERS - INSTALLED** セクション
- 各サーバーの状態管理：
  - ✅ Start Server / Stop Server / Restart Server
  - 📋 Show Output (ログ表示)
  - ⚙️ Show Configuration (設定表示)
  - 🔗 Configure Model Access (モデルアクセス管理)
  - 📊 Show Sampling Requests (デバッグ用)
  - 📁 Browse Resources (リソース参照)
  - 🗑️ Uninstall (アンインストール)

#### Dev Container対応
`devcontainer.json` で直接MCP設定が可能：

```json
{
  "image": "mcr.microsoft.com/devcontainers/python:latest",
  "customizations": {
    "vscode": {
      "mcp": {
        "servers": {
          "corethink-mcp": {
            "command": "python",
            "args": ["src/corethink_mcp/server/corethink_server.py"],
            "cwd": "/workspaces/CoreThink-MCP"
          }
        }
      }
    }
  }
}
```

#### プロファイル対応
- 各VS Codeプロファイルごとに異なるMCPサーバー設定が可能
- Settings Syncでプロファイル間での設定同期対応
- チーム・プロジェクト別のMCPサーバー構成管理

#### 移行サポート
既存の `settings.json` にMCP設定がある場合：
- **自動検出**: VS Codeが既存設定を自動で検出
- **リアルタイム移行**: 新しい `mcp.json` 形式に自動変換
- **通知表示**: 移行完了時に説明付き通知
- **クロスプラットフォーム**: ローカル、リモート、WSL、Codespacesすべて対応

</details>

<details>
<summary>🖥️ LM Studio (v0.3.17以降) 設定</summary>

**LM Studio はローカルLLMとMCPを組み合わせた強力な開発環境を提供します！**

### ワンクリックインストール 🚀

**最も簡単な方法:** ボタンをクリックして自動インストール

**標準Python環境:**

[![Add CoreThink-MCP to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInB5dGhvbiIsICJhcmdzIjogWyJzcmMvY29yZXRoaW5rX21jcC9zZXJ2ZXIvY29yZXRoaW5rX3NlcnZlci5weSJdLCAiY3dkIjogIi9hYnNvbHV0ZS9wYXRoL3RvL3lvdXIvQ29yZVRoaW5rLU1DUCJ9fQ==)

**UV環境:**

[![Add CoreThink-MCP (UV) to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp-uv&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInV2IiwgImFyZ3MiOiBbInJ1biIsICJweXRob24iLCAic3JjL2NvcmV0aGlua19tY3Avc2VydmVyL2NvcmV0aGlua19zZXJ2ZXIucHkiXSwgImN3ZCI6ICIvYWJzb2x1dGUvcGF0aC90by95b3VyL0NvcmVUaGluay1NQ1AifX0=)

**⚠️ 重要**: インストール後、LM Studio で `cwd` のパスを必ずあなたの環境に合わせて変更してください。

### 手動設定

**必要バージョン**: LM Studio 0.3.17 (b10) 以降

#### 設定手順
1. **LM Studio を起動**
2. **Program タブ** を開く (右サイドバー)
3. **Install > Edit mcp.json** をクリック
4. エディタで以下の設定を追加：

```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "python",
      "args": ["src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP"
    }
  }
}
```

#### UV環境使用の場合
```json
{
  "mcpServers": {
    "corethink-mcp": {
      "command": "uv",
      "args": ["run", "python", "src/corethink_mcp/server/corethink_server.py"],
      "cwd": "/YOUR_ABSOLUTE_PATH/CoreThink-MCP"
    }
  }
}
```

### LM Studio の特徴

#### 完全ローカル実行
- **プライバシー**: データが外部に送信されない
- **オフライン対応**: インターネット接続不要
- **高速処理**: ローカルGPUを活用した高速推論

#### カスタマイズ性
- **モデル選択**: Llama, Mistral, CodeLlama など自由選択
- **パラメータ調整**: Temperature, Top-p, Max tokens などの調整
- **プリセット**: チーム・プロジェクト別の設定プリセット

#### セキュリティ
- **コード保護**: コードが外部サービスに送信されない
- **企業対応**: 機密情報の漏洩リスクなし
- **アクセス制御**: MCP サーバーの権限管理

### 使用方法

#### チャットでの利用
1. **LM Studio でモデルをロード**
2. **Chat タブ** でコードに関する質問
3. **CoreThink-MCP ツール** が自動で利用可能
4. **GSR推論・制約検証・安全実行** をローカルで実行

#### 推奨モデル

**コード生成・編集向け:**
- CodeLlama 13B/34B
- Llama 3.1 8B/70B Instruct
- Mistral 7B/22B Instruct
- DeepSeek Coder V2

**日本語対応:**
- Japanese Stable LM 3B/7B
- ELYZA japanese-llama-2-7b/13b

</details>

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

## ⚙️ 高度な設定

### 環境変数 (.env)

```bash
CORETHINK_REPO_ROOT=.              # 対象リポジトリ
CORETHINK_LOG_LEVEL=INFO           # ログレベル
CORETHINK_PORT=8080                # サーバーポート
CORETHINK_SANDBOX_DIR=.sandbox     # サンドボックス名
```

### 制約ファイル (constraints.txt)

```txt
MUST: 公開APIの変更を禁止
NEVER: printやconsole.logなどのデバッグ出力を追加しない
SHOULD: 関数変更時はdocstringを更新する
MUST: すべてのテストがパスすること
```

## 🔧 トラブルシューティング

### 動作確認

#### サーバーの手動起動テスト

```bash
# プロジェクトディレクトリで実行
cd /YOUR_ABSOLUTE_PATH/CoreThink-MCP

# UV環境の場合
uv run python src/corethink_mcp/server/corethink_server.py

# 標準Python環境の場合
.venv/bin/python src/corethink_mcp/server/corethink_server.py  # Unix
.venv\Scripts\python src/corethink_mcp/server/corethink_server.py  # Windows
```

#### MCPテストクライアント

```bash
python test_mcp_client.py
```

正常に動作している場合、以下のような出力が表示されます：

```txt
=== Tool: reason_about_change ===
【判定】PROCEED
【理由】制約適合性確認済み
【次ステップ】実装推奨

=== Tool: validate_against_constraints ===
✅ MUST: 必須制約適合
❌ NEVER: 禁止制約なし
⚠️ SHOULD: 推奨制約確認

=== Tool: execute_with_safeguards ===
【DRY RUN】サンドボックスで安全実行
変更ファイル: example.py
実ファイルに影響なし
```

### よくある問題

#### 問題1: "command not found" エラー

**原因**: パスが正しく設定されていない

**解決策**:
1. 絶対パスを確認: `pwd` (Unix) または `echo %CD%` (Windows)
2. Python実行可能ファイルのパスを確認: `which python` (Unix) または `where python` (Windows)

#### 問題2: "Module not found" エラー

**原因**: 依存関係がインストールされていない

**解決策**:
```bash
# UV環境
uv sync

# 標準環境
pip install -e .
```

#### 問題3: Claude Desktopで認識されない

**原因**: 設定ファイルの JSON 構文エラーまたはパス間違い

**解決策**:
1. JSON構文チェック: [jsonlint.com](https://jsonlint.com/)
2. パスの確認（絶対パス、区切り文字）
3. Claude Desktopの再起動

#### 問題4: VS Code でサーバーが起動しない

**原因**: MCP設定ファイルの権限またはパス問題

**解決策**:
1. MCP設定ファイルの権限確認
2. 絶対パスの使用
3. VS Code の再起動

#### 問題5: LM Studio で接続できない

**原因**: LM Studio のバージョンまたは設定問題

**解決策**:
1. LM Studio 0.3.17 (b10) 以降を使用
2. `mcp.json` の構文確認
3. フォルダー権限の確認

### デバッグ方法

- **ログ確認**: `logs/trace.log` でサーバーログを確認
- **手動実行**: ターミナルでMCPサーバーを直接起動してテスト
- **設定検証**: JSON構文エラーチェック

### サポート

問題が解決しない場合は、以下の情報と共にIssueを作成してください：

- OS とバージョン
- Python バージョン (`python --version`)
- エラーメッセージの全文
- 使用した設定ファイル（パスは伏字で）

[GitHub Issues](https://github.com/kechirojp/CoreThink-MCP/issues)

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
