---
applyTo: "**"
---
# Model Context Protocol (MCP) サーバー開発ルール

## MCP プロトコル基本原則

このファイルは、memoryMCPサーバー開発時にModel Context Protocol (MCP) の仕様を忘れないための重要なルールをまとめています。

## アーキテクチャの基本

### 参加者の役割

- **MCP Host**: AI アプリケーション（VS Code、Claude Desktop など）
- **MCP Client**: ホストが各サーバーとの接続を管理するコンポーネント
- **MCP Server**: コンテキストを提供するプログラム（我々のlong_memory_MCPサーバー）

### 接続関係

- MCP Host は複数の MCP Server に接続可能
- 各 MCP Server に対して専用の MCP Client を作成
- **1対1の関係**: 1つのMCPクライアント = 1つのMCPサーバー

## プロトコル層の構造

### データ層（内側）

- **JSON-RPC 2.0** ベースのプロトコル
- ライフサイクル管理（接続初期化、能力交渉、終了）
- プリミティブ（tools、resources、prompts）
- 通知システム

### トランスポート層（外側）

- **STDIO Transport**: 標準入出力（ローカル通信用）
- **HTTP Transport**: HTTP POST + Server-Sent Events（リモート通信用）

## 重要な実装ルール

### 1. ログ出力の禁止事項

```python
# ❌ 絶対にやってはいけない（STDIOが壊れる）
print("Processing request")
console.log("Debug info")

# ✅ 正しい方法
import logging
logging.info("Processing request")  # stderrに出力
```

### 2. JSON-RPC 2.0 メッセージ形式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {}
  }
}
```

### 3. 必須のライフサイクル管理

#### 初期化シーケンス

1. クライアント → `initialize` リクエスト
2. サーバー → 能力情報を含むレスポンス
3. クライアント → `notifications/initialized` 通知

#### 能力交渉の例

```json
{
  "capabilities": {
    "tools": {"listChanged": true},
    "resources": {},
    "prompts": {}
  }
}
```

## MCPプリミティブの実装

### サーバーが提供できるプリミティブ

#### 1. Tools（実行可能な機能）

```python
# tools/list - 利用可能なツールの一覧
# tools/call - ツールの実行
```

#### 2. Resources（データソース）

```python
# resources/list - 利用可能なリソースの一覧
# resources/read - リソースの読み取り
```

#### 3. Prompts（テンプレート）

```python
# prompts/list - 利用可能なプロンプトの一覧
# prompts/get - プロンプトの取得
```

### クライアントが提供できるプリミティブ

#### 1. Sampling（LLM補完要求）

```python
# sampling/complete - 言語モデルからの補完を要求
```

#### 2. Elicitation（ユーザー入力要求）

```python
# elicitation/request - ユーザーからの追加情報を要求
```

#### 3. Logging（ログ送信）

```python
# logging/log - クライアントへのログメッセージ送信
```

## 通知システムの実装

### 動的更新の通知

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

**重要**: 通知には `id` フィールドを含めない（レスポンス不要）



## 参考リンク

- [MCP Architecture](https://modelcontextprotocol.io/docs/learn/architecture)
- [Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [Client Quickstart](https://modelcontextprotocol.io/quickstart/client)
- [Remote MCP Server Tutorial](https://modelcontextprotocol.io/docs/tutorials/use-remote-mcp-server)
