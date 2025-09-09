# 🚀 CoreThink-MCP Node.js対応 - 実装ガイド

## 📋 現状と方針

### ✅ 現在の実装状況（Python版 v1.0.0）
- **完全実装済み**: 9ツール + 2リソース
- **マルチプラットフォーム対応**: Claude Desktop, VS Code, LM Studio
- **配布システム**: .DXT, Setup Helper, Remote MCP

### 🎯 Node.js対応の目標
- **npm生態系統合**: `npx @corethink/mcp@latest` でワンクリックインストール
- **VS Code公式対応**: ボタンクリックでのインストール
- **ハイブリッド実装**: Node.jsプロキシ + Python推論エンジン

## 🛠 実装アーキテクチャ

### ハイブリッド版のメリット
1. **既存資産活用**: Python版の完全実装を再利用
2. **迅速な対応**: 新規実装不要で短期対応可能
3. **品質保証**: 実証済みのGSR推論エンジンを維持
4. **段階的移行**: 将来的な純TypeScript化への道筋

### システム構成
```
MCP Client (VS Code/Claude/etc)
        ↓ STDIO/HTTP
Node.js Proxy Server (@corethink/mcp)
        ↓ subprocess + JSON
Python CoreThink-MCP Engine
        ↓ GSR Processing
Results back through chain
```

## 📦 実装ファイル構成

### Node.jsパッケージ構造
```
nodejs/
├── package.json              # NPM設定
├── tsconfig.json             # TypeScript設定
├── src/
│   ├── index.ts             # メインサーバークラス
│   ├── bin/
│   │   └── corethink-mcp.ts  # CLI エントリーポイント
│   └── types/
│       └── corethink.ts      # 型定義
├── dist/                     # ビルド成果物
└── README.md                # Node.js版説明
```

### Python CLIインターフェース
```
src/corethink_mcp/
└── cli.py                   # Node.js → Python bridge
```

## 🔧 セットアップ手順

### 1. Node.js環境準備
```bash
cd CoreThink-MCP
mkdir -p nodejs
cd nodejs
```

### 2. 依存関係インストール
```bash
npm install @modelcontextprotocol/sdk
npm install -D typescript @types/node ts-node
```

### 3. Python CLI準備
```bash
# Python仮想環境に入る
source .venv/Scripts/activate  # Windows
# または
source .venv/bin/activate      # macOS/Linux

# CLIテスト
python src/corethink_mcp/cli.py --tool reason_about_change --args '{"change_description": "Test change"}'
```

## 🎯 VS Code ワンクリック対応

### インストールボタンURL
```typescript
const installURL = `vscode:mcp/install?${encodeURIComponent(JSON.stringify({
  "name": "corethink",
  "command": "npx",
  "args": ["@corethink/mcp@latest"]
}))}`;
```

### 設定ファイル自動生成
```json
{
  "mcpServers": {
    "corethink": {
      "command": "npx",
      "args": ["@corethink/mcp@latest"]
    }
  }
}
```

## 🧪 テスト手順

### 1. Python CLI単体テスト
```bash
cd CoreThink-MCP
source .venv/Scripts/activate

# ツール実行テスト
python src/corethink_mcp/cli.py \
  --tool reason_about_change \
  --args '{"change_description": "Add new validation function"}'
```

### 2. Node.js プロキシテスト
```bash
cd nodejs
npm run build
node dist/bin/corethink-mcp.js
```

### 3. 統合テスト
```bash
# MCPクライアントでの接続テスト
npx @modelcontextprotocol/inspector node dist/bin/corethink-mcp.js
```

## 📊 性能・互換性

### 期待される性能
- **起動時間**: ~2秒（プロキシ + Python初期化）
- **応答時間**: Python版 + ~100ms（プロキシオーバーヘッド）
- **メモリ使用量**: ~100MB（Node.js + Python両方）

### 互換性マトリクス
| 環境 | Node.js版 | Python版 | 備考 |
|------|-----------|----------|------|
| VS Code 1.102+ | ✅ | ✅ | ワンクリック vs 手動設定 |
| Claude Desktop | ✅ | ✅ | 同等の機能 |
| LM Studio | ✅ | ✅ | 設定方法のみ違い |
| Cursor | ✅ | ✅ | MCP設定同様 |

## 🚀 段階的展開計画

### Phase 1: 基盤構築（1週間）
- [x] パッケージ構造設計完了
- [x] Python CLI実装完了
- [ ] Node.jsプロキシ実装
- [ ] 基本動作確認

### Phase 2: パッケージ公開（1週間）
- [ ] NPMパッケージビルド
- [ ] @corethink/mcp 公開
- [ ] インストール手順検証
- [ ] ドキュメント整備

### Phase 3: VS Code統合（1週間）
- [ ] VS Code Gallery申請
- [ ] ワンクリックボタン実装
- [ ] 公式ドキュメント更新
- [ ] コミュニティフィードバック対応

## ⚠️ 既知の制約・課題

### 技術的制約
- **依存関係**: Node.js + Python両方必要
- **起動時間**: プロキシ分の遅延
- **エラー伝播**: 2層構造でのデバッグ複雑性

### 対応策
- **依存関係**: インストールガイドの充実
- **起動時間**: Python プロセス再利用の検討
- **エラー伝播**: 詳細ログとエラーコード体系

## 🎯 将来的な移行計画

### Pure TypeScript版への道筋
1. **Phase 1**: ハイブリッド版での実績積累
2. **Phase 2**: 核心ロジックのTypeScript移植
3. **Phase 3**: パフォーマンス最適化
4. **Phase 4**: Python依存関係除去

### 判断基準
- **利用実績**: 月間アクティブユーザー
- **性能要求**: レスポンス時間・メモリ使用量
- **開発工数**: 移植コスト vs メンテナンス負荷

---

**🚀 この実装により、CoreThink-MCPはJavaScript/TypeScript開発者にも広く利用可能になり、GSR（General Symbolics Reasoning）の普及が加速します。**
