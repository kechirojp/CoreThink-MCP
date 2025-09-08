# 🛠 CoreThink-MCP セットアップガイド

このガイドでは、CoreThink-MCPサーバーを様々な環境で設定する方法を説明します。

## 📋 前提条件

- Python 3.11以上
- Git
- Claude Desktop または VS Code + MCP Extension

## 🚀 インストール手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP
```

### 2. 環境セットアップ

#### オプションA: UV使用（推奨）

```bash
# UVをインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール
uv sync
```

#### オプションB: 標準Python環境

```bash
# 仮想環境作成
python -m venv .venv

# 仮想環境のアクティベート
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 依存関係のインストール
pip install -e .
```

## ⚙️ Claude Desktop設定

### 1. 設定ファイルの場所

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

### 2. 設定内容

#### UV環境の場合

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

#### 標準Python環境の場合

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

### 3. パス設定の重要事項

**⚠️ 重要**: 必ず以下の点を確認してください：

1. `cwd` フィールドには、CoreThink-MCPプロジェクトの**絶対パス**を指定
2. パスの区切り文字は OS に応じて調整:
   - **Windows**: `C:\\Users\\YourName\\CoreThink-MCP`
   - **macOS/Linux**: `/home/yourname/CoreThink-MCP`
3. 仮想環境を使用する場合は、`env.PATH` を適切に設定

## 🔧 VS Code設定 (v1.102以降対応) 🆕

**VS Code 1.102以降では、MCPサポートが正式版となり、大幅に改善されました！**

### 1. 推奨方法: MCP Servers ギャラリー

VS Code 1.102以降では、MCP Serversの管理が大幅に簡単になりました：

1. **拡張機能ビューを開く**: `Ctrl+Shift+X` (Windows/Linux) または `Cmd+Shift+X` (macOS)
2. **MCP SERVERS** セクションを探す
3. **Browse MCP Servers...** をクリック
4. [VS Code MCP ギャラリー](https://code.visualstudio.com/mcp) でCoreThink-MCPを検索
5. **Install** ボタンをクリックして自動インストール

### 2. 手動設定方法

#### 設定ファイルアクセス

```bash
# ユーザー設定ファイルを開く
Ctrl+Shift+P → "MCP: Open User Configuration"

# リモート環境の場合
Ctrl+Shift+P → "MCP: Open Remote User Configuration"
```

#### 設定内容 (mcp.json)

**VS Code 1.102以降では、MCPサーバーは `mcp.json` ファイルで管理されます：**

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

**UV環境の場合:**

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

### 3. 新機能 (VS Code 1.102+)

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

### 4. 移行サポート

既存の `settings.json` にMCP設定がある場合：

- **自動検出**: VS Codeが既存設定を自動で検出
- **リアルタイム移行**: 新しい `mcp.json` 形式に自動変換
- **通知表示**: 移行完了時に説明付き通知
- **クロスプラットフォーム**: ローカル、リモート、WSL、Codespacesすべて対応

## 🎯 LM Studio設定 (v0.3.17以降対応) 🆕

**LM Studio はローカルLLMとMCPを組み合わせた強力な開発環境を提供します！**

### 1. ワンクリックインストール 🚀

**最も簡単な方法:** ボタンをクリックして自動インストール

**標準Python環境:**

[![Add CoreThink-MCP to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInB5dGhvbiIsICJhcmdzIjogWyJzcmMvY29yZXRoaW5rX21jcC9zZXJ2ZXIvY29yZXRoaW5rX3NlcnZlci5weSJdLCAiY3dkIjogIi9hYnNvbHV0ZS9wYXRoL3RvL3lvdXIvQ29yZVRoaW5rLU1DUCJ9fQ==)

**UV環境:**

[![Add CoreThink-MCP (UV) to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp-uv&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInV2IiwgImFyZ3MiOiBbInJ1biIsICJweXRob24iLCAic3JjL2NvcmV0aGlua19tY3Avc2VydmVyL2NvcmV0aGlua19zZXJ2ZXIucHkiXSwgImN3ZCI6ICIvYWJzb2x1dGUvcGF0aC90by95b3VyL0NvcmVUaGluay1NQ1AifX0=)

**⚠️ 重要**: インストール後、LM Studio で `cwd` のパスを必ずあなたの環境に合わせて変更してください。

### 2. 手動設定

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

### 2. LM Studio の特徴

#### 🖥️ 完全ローカル実行
- **プライバシー**: データが外部に送信されない
- **オフライン対応**: インターネット接続不要
- **高速処理**: ローカルGPUを活用した高速推論

#### 🔧 カスタマイズ性
- **モデル選択**: Llama, Mistral, CodeLlama など自由選択
- **パラメータ調整**: Temperature, Top-p, Max tokens などの調整
- **プリセット**: チーム・プロジェクト別の設定プリセット

#### 🛡️ セキュリティ
- **コード保護**: コードが外部サービスに送信されない
- **企業対応**: 機密情報の漏洩リスクなし
- **アクセス制御**: MCP サーバーの権限管理

### 3. 使用方法

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

### 4. トラブルシューティング

#### よくある問題

**問題1**: MCP サーバーが認識されない
- **解決策**: `mcp.json` のパス確認、LM Studio 再起動

**問題2**: Python環境が見つからない
- **解決策**: 仮想環境のアクティベート、絶対パス指定

**問題3**: 権限エラー
- **解決策**: フォルダー権限確認、管理者権限での実行

#### デバッグ方法

- **ログ確認**: LM Studio の Developer Tools でコンソール確認
- **手動実行**: ターミナルでMCPサーバーを直接起動してテスト
- **設定検証**: JSON構文エラーチェック

## ✅ 動作確認

### 1. サーバーの手動起動テスト

```bash
# プロジェクトディレクトリで実行
cd /YOUR_ABSOLUTE_PATH/CoreThink-MCP

# UV環境の場合
uv run python src/corethink_mcp/server/corethink_server.py

# 標準Python環境の場合
.venv/bin/python src/corethink_mcp/server/corethink_server.py  # Unix
.venv\Scripts\python src/corethink_mcp/server/corethink_server.py  # Windows
```

### 2. MCPテストクライアント

```bash
python test_mcp_client.py
```

正常に動作している場合、以下のような出力が表示されます：

```
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

## 🐛 トラブルシューティング

### 問題1: "command not found" エラー

**原因**: パスが正しく設定されていない

**解決策**:
1. 絶対パスを確認: `pwd` (Unix) または `echo %CD%` (Windows)
2. Python実行可能ファイルのパスを確認: `which python` (Unix) または `where python` (Windows)

### 問題2: "Module not found" エラー

**原因**: 依存関係がインストールされていない

**解決策**:
```bash
# UV環境
uv sync

# 標準環境
pip install -e .
```

### 問題3: Claude Desktopで認識されない

**原因**: 設定ファイルの JSON 構文エラーまたはパス間違い

**解決策**:
1. JSON構文チェック: https://jsonlint.com/
2. パスの確認（絶対パス、区切り文字）
3. Claude Desktopの再起動

## 📞 サポート

問題が解決しない場合は、以下の情報と共にIssueを作成してください：

- OS とバージョン
- Python バージョン (`python --version`)
- エラーメッセージの全文
- 使用した設定ファイル（パスは伏字で）

GitHub Issues: https://github.com/kechirojp/CoreThink-MCP/issues
