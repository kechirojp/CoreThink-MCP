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
