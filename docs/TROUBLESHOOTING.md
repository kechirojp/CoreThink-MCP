# 🔧 CoreThink-MCP トラブルシューティング・FAQ

## 🎯 SWE-Bench実証に基づく技術的問題解決

CoreThink-MCPはSWE-Bench Liteにおいて62.3%の成功率を達成し、従来手法を5.6ポイント上回る性能を示しました。この技術的優位性を活用した体系的なトラブルシューティング手法を解説します。

---

## ❓ よくある質問（FAQ）

### 🚀 インストール・設定関連

#### Q1: 「MCP server not found」エラーが出る

**症状**: Claude Desktop や VS Code で CoreThink-MCP が認識されない

**原因**: 設定ファイルが正しい場所に配置されていない

**解決方法**:

```bash
# 1. 設定確認
python setup_helper.py --check

# 2. 設定ファイルの場所を表示
python setup_helper.py --show-config

# 3. 設定を再実行
python setup_helper.py --reset
```

**具体例**:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

---

#### Q2: Python の依存関係エラーが出る

**症状**: `ModuleNotFoundError` や `ImportError` が発生

**原因**: 必要なパッケージがインストールされていない

**解決方法**:

```bash
# 1. 仮想環境を確認
python -c "import sys; print(sys.prefix)"

# 2. 依存関係を再インストール
pip install --upgrade pip
pip install --force-reinstall -e .

# 3. 問題のあるパッケージを個別インストール
pip install fastmcp mcp gitpython
```

---

#### Q3: 推論が遅い、タイムアウトする

**症状**: 推論に数十秒かかる、または途中で停止する

**原因**: GSR推論の深度が高い、または複雑な分野制約が適用されている

**解決方法**:

```bash
# 1. 機能フラグで軽量化モードに変更
echo "lightweight_mode: true" >> conf/feature_flags.yaml

# 2. 推論深度を調整
echo "max_reasoning_depth: 3" >> conf/feature_flags.yaml

# 3. 特定分野の制約を無効化（テスト用）
echo "domain_detection: false" >> conf/feature_flags.yaml
```

---

## 🔍 高度なトラブルシューティング

### 技術的根本原因分析プロセス

#### Phase 1: 問題の理解と分析

**1. 症状の詳細収集**
```
エラーメッセージ・ログの収集
→ 再現条件の特定
→ 影響範囲の確認
```

**2. システム状態の確認**
```bash
# ログファイルの確認
cat logs/trace.log | tail -50

# 推論履歴の確認
cat logs/reasoning_history.md | tail -100

# 機能フラグの状態確認
cat conf/feature_flags.yaml
```

#### Phase 2: 根本原因の特定

**SWE-Bench準拠の系統的アプローチ**：

1. **制約充足問題として定式化**
   - 何が期待されているか？
   - 何が実際に起こっているか？
   - どこに矛盾があるか？

2. **依存関係の分析**
   - モジュール間の依存関係チェック
   - 設定ファイルの整合性確認
   - 外部ツールとの互換性検証

3. **実行パスの追跡**
   - GSR推論の各層での処理確認
   - 制約適用のタイミング検証
   - サンドボックス隔離の動作確認

#### Phase 3: 解決策の実装

**保守性重視の修正アプローチ**：

1. **最小限の変更**
   - 影響範囲を限定した修正
   - 既存機能への副作用回避
   - テストケースでの動作確認

2. **段階的な検証**
   - dry-run モードでの事前検証
   - サンドボックス環境での安全テスト
   - 本番環境への段階的適用

---

## 🚨 緊急時対応プロトコル

### システム異常時の即座対応

```bash
# 緊急停止（全機能無効化）
python -c "
from src.corethink_mcp.feature_flags import feature_flags
feature_flags.emergency_disable()
print('🚨 緊急モード: 全拡張機能を無効化しました')
"

# 設定リセット
python setup_helper.py --reset --force

# ログクリア（必要に応じて）
rm -f logs/trace.log logs/reasoning_history.md
```

### 本番環境での安全運用

**1. 事前検証の徹底**
```bash
# サンドボックステスト
python -c "
from src.corethink_mcp.server.corethink_server import create_sandbox
sandbox_path = create_sandbox()
print(f'テスト環境: {sandbox_path}')
"
```

**2. 監視とアラート**
```bash
# ログ監視
tail -f logs/trace.log | grep -E "(ERROR|CRITICAL)"

# 推論時間監視
tail -f logs/reasoning_history.md | grep -E "実行時間"
```

---

## 📞 コミュニティサポート

### 効果的な質問の仕方

**良い質問例**:
```
【環境】: Windows 11, Python 3.11, Claude Desktop
【現象】: 医療分野での推論が途中で停止
【エラー】: [具体的なエラーメッセージ]
【試したこと】: 設定リセット、依存関係再インストール
【ログ】: [trace.logの関連部分]
```

**避けるべき質問**:
- "動かない"だけの報告
- 環境情報なしの質問
- ログを確認していない状態での質問

### リソース

- **GitHub Issues**: バグレポート・機能要望
- **論文参照**: [arXiv:2509.00971v2](https://arxiv.org/abs/2509.00971)
- **技術文書**: `docs/` フォルダ内の専門ガイド

---

**💡 問題解決のコツ**: CoreThink-MCPは学術研究ベースのシステムです。問題解決時も「なぜそうなるか」の理論的理解を重視してください。表面的な回避策ではなく、根本的な解決を目指しましょう。