# LM Studio用 CoreThink-MCP設定

## 設定JSON (手動用)

```json
{
  "corethink-mcp": {
    "command": "python",
    "args": ["src/corethink_mcp/server/corethink_server.py"],
    "cwd": "/absolute/path/to/your/CoreThink-MCP"
  }
}
```

## UV環境用設定

```json
{
  "corethink-mcp": {
    "command": "uv", 
    "args": ["run", "python", "src/corethink_mcp/server/corethink_server.py"],
    "cwd": "/absolute/path/to/your/CoreThink-MCP"
  }
}
```

## Deeplink生成用

上記のJSONを https://lmstudio.ai/docs/app/plugins/mcp/deeplink でbase64エンコードして、
LM Studio用のワンクリックインストールリンクを生成できます。

## 注意事項

- `cwd` パスは必ず絶対パスで指定
- Python環境が正しくセットアップされていることを確認
- LM Studio 0.3.17以降が必要
