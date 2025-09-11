# 🔧 CoreThink-MCP インストールガイド

## 📍 VS Code MCP設定ファイルの場所

各OSで以下の場所にある `mcp.json` ファイルを編集してください：

### Windows
```
C:\Users\<username>\AppData\Roaming\Code\User\mcp.json
```

### macOS
```
~/Library/Application Support/Code/User/mcp.json
```

### Linux
```
~/.config/Code/User/mcp.json
```

## 🛠 OS別設定方法

### 1. Windows設定

1. `install/mcp.json.windows` の内容をコピー
2. `C:\Users\<username>\AppData\Roaming\Code\User\mcp.json` に追加
3. `C:\\Path\\To\\CoreThink-MCP` を実際のパスに変更

```jsonc
{
	"servers": {
		"CoreThink-MCP": {
			"type": "stdio",
			"command": "uv",
			"args": [
				"run",
				"--directory",
				"C:\\Users\\owner\\CoreThink-MCP",  // 実際のパスに変更
				"python",
				"-m",
				"src.corethink_mcp.server.corethink_server"
			],
			"env": {
				"PYTHONIOENCODING": "utf-8"
			}
		}
	}
}
```

### 2. macOS設定

1. `install/mcp.json.macos` の内容をコピー
2. `~/Library/Application Support/Code/User/mcp.json` に追加
3. `/path/to/CoreThink-MCP` を実際のパスに変更

```jsonc
{
	"servers": {
		"CoreThink-MCP": {
			"type": "stdio",
			"command": "uv",
			"args": [
				"run",
				"--directory",
				"/Users/username/CoreThink-MCP",  // 実際のパスに変更
				"python",
				"-m",
				"src.corethink_mcp.server.corethink_server"
			],
			"env": {
				"PYTHONIOENCODING": "utf-8"
			}
		}
	}
}
```

### 3. Linux設定

1. `install/mcp.json.linux` の内容をコピー
2. `~/.config/Code/User/mcp.json` に追加
3. `/home/user/CoreThink-MCP` を実際のパスに変更

```jsonc
{
	"servers": {
		"CoreThink-MCP": {
			"type": "stdio",
			"command": "uv",
			"args": [
				"run",
				"--directory",
				"/home/username/CoreThink-MCP",  // 実際のパスに変更
				"python",
				"-m",
				"src.corethink_mcp.server.corethink_server"
			],
			"env": {
				"PYTHONIOENCODING": "utf-8"
			}
		}
	}
}
```

## ⚠️ 重要な注意事項

1. **パスの書き換え**: 各OSのテンプレートのパス部分を必ず実際のインストール場所に変更してください
2. **スラッシュの向き**: Windowsは `\\`、macOS/Linuxは `/` を使用
3. **既存設定の保持**: 既に他のMCPサーバー設定がある場合は、`servers` セクションに追加してください
4. **文字化け対策**: `PYTHONIOENCODING: utf-8` は必須です

## 🔍 設定確認方法

1. VS Codeを再起動
2. コマンドパレット（Ctrl+Shift+P / Cmd+Shift+P）
3. "MCP: List Servers" を実行
4. "CoreThink-MCP" が表示されれば成功

## 🚨 トラブルシューティング

### エラー: "command not found: uv"
```bash
# uvをインストール
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix系
# または
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

### エラー: "Module not found"
```bash
# プロジェクトディレクトリで依存関係をインストール
cd /path/to/CoreThink-MCP
uv sync
```

### 文字化け問題
- `PYTHONIOENCODING: utf-8` 設定が正しく追加されているか確認
- VS Codeを完全に再起動

## 📝 設定例（完全版）

他のMCPサーバーと併用する場合の設定例：

```jsonc
{
	"servers": {
		"github": {
			"command": "docker",
			"args": ["run", "-i", "--rm", "ghcr.io/github/github-mcp-server"],
			"type": "stdio"
		},
		"CoreThink-MCP": {
			"type": "stdio",
			"command": "uv",
			"args": [
				"run",
				"--directory",
				"/your/actual/path/CoreThink-MCP",
				"python",
				"-m",
				"src.corethink_mcp.server.corethink_server"
			],
			"env": {
				"PYTHONIOENCODING": "utf-8"
			}
		}
	}
}
```
