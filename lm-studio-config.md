# LM Studio用 CoreThink-MCP設定

## 🚀 ワンクリックインストール

**最も簡単な方法:** 以下のボタンをクリックして自動インストール

### 標準Python環境

[![Add CoreThink-MCP to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInB5dGhvbiIsICJhcmdzIjogWyJzcmMvY29yZXRoaW5rX21jcC9zZXJ2ZXIvY29yZXRoaW5rX3NlcnZlci5weSJdLCAiY3dkIjogIi9hYnNvbHV0ZS9wYXRoL3RvL3lvdXIvQ29yZVRoaW5rLU1DUCJ9fQ==)

### UV環境

[![Add CoreThink-MCP (UV) to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](lmstudio://add_mcp?name=corethink-mcp-uv&config=eyJjb3JldGhpbmstbWNwIjogeyJjb21tYW5kIjogInV2IiwgImFyZ3MiOiBbInJ1biIsICJweXRob24iLCAic3JjL2NvcmV0aGlua19tY3Avc2VydmVyL2NvcmV0aGlua19zZXJ2ZXIucHkiXSwgImN3ZCI6ICIvYWJzb2x1dGUvcGF0aC90by95b3VyL0NvcmVUaGluay1NQ1AifX0=)

**⚠️ 重要**: インストール後、LM Studio の mcp.json エディタで `cwd` のパスを必ずあなたの環境に合わせて変更してください。

## 📋 手動設定用JSON

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
