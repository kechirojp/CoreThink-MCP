# 🚀 CoreThink-MCP はじめに・活用ガイド

## 🎯 まず確認：あなたはどちらのタイプ？

### 👨‍💼 すぐに業務で使いたい → **5分で開始**
- **推奨**: Claude Desktop + DXT方式（最も簡単）
- **目的**: 即座に専門分野の判断支援を受けたい

### 👨‍💻 技術的に理解して使いたい → **10分で開始**  
- **推奨**: Python環境セットアップ（カスタマイズ可能）
- **目的**: 仕組みを理解して最適化したい

---

## ⚡ 5分で開始：Claude Desktop + DXT方式

### Step 1: リポジトリを取得

```bash
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP
```

### Step 2: DXTパッケージを生成

```bash
python -m zipfile -c corethink-mcp.dxt src/ *.md LICENSE
```

### Step 3: Claude Desktopにドラッグ&ドロップ

1. `corethink-mcp.dxt` ファイルを Claude Desktop にドラッグ
2. 「MCP Server を追加」をクリック  
3. 完了！

### Step 4: 動作確認

Claude Desktopで以下を試してください：

```
医療診断における安全性について分析してください
```

✅ **成功**: 医療分野の専門制約が適用された詳細分析が表示される  
❌ **失敗**: [トラブルシューティング](TROUBLESHOOTING.md)をご確認ください

---

## 🔧 10分で開始：uv環境セットアップ

### 前提条件

- Python 3.11以上
- Git
- **uv**（高速Pythonパッケージマネージャー）

### Step 1: uvのインストール（まだの場合）

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# pip経由（全プラットフォーム）
pip install uv
```

### Step 2: プロジェクトセットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP

# 2. uvで依存関係を自動解決・インストール
uv sync

# 3. 自動設定を実行
uv run python setup_helper.py
```

**uvの利点**：
- ⚡ **高速**: pipより10-100倍高速
- 🔒 **確実**: ロックファイル（uv.lock）で再現性確保
- 🎯 **簡単**: 仮想環境管理が自動化

### Step 3: 動作確認

```bash
# サーバー起動テスト
uv run python -m src.corethink_mcp.server.corethink_server

# VS Code での確認
code .
```

### 従来のPython環境でのセットアップ（uv推奨）

uvがインストールできない場合の代替手順：

```bash
# 1. リポジトリをクローン
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP

# 2. 仮想環境を作成・有効化
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 3. 依存関係をインストール
pip install --upgrade pip
pip install -e .

# 4. 自動設定を実行
python setup_helper.py
```

VS Code で以下を実行：

```python
# コード分析の例
analyze_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

# CoreThink-MCPに分析を依頼（uvコマンド使用）
# uv run python -c "import src.corethink_mcp; ..."
```

---

## 💡 実際の使用例

### 🏥 医療現場での使用例

**入力例**:
```
患者の症状：発熱38.5℃、咳、息切れ
鑑別診断の検討をお願いします
```

**期待される出力**:
- 医療安全制約の自動適用
- 複数の鑑別診断候補
- 追加検査の推奨
- 緊急度の評価

### ⚖️ 法律分野での使用例

**入力例**:
```
業務委託契約書の以下の条項について法的リスクを分析してください：
「乙は甲の指示に従い...」
```

**期待される出力**:
- 法的制約の自動適用
- 偽装請負リスクの評価
- 改善提案
- 関連法令の参照

### 💰 金融分野での使用例

**入力例**:
```
新規融資案件の審査において、以下の財務データを評価してください：
売上高：1億円、営業利益率：5%...
```

**期待される出力**:
- 金融規制制約の適用
- リスク要因の特定
- 融資可否の判断材料
- 金利設定の考慮事項

---

## 🎯 このツールが適している人・適さない人

### ✅ 強く推奨される用途

**高度な専門知識が必要な判断**：
- **医療従事者**: 診断支援・治療計画策定
- **法律専門家**: 契約書レビュー・法的リスク分析  
- **ソフトウェアエンジニア**: 複雑なシステム設計・バグ修正
- **金融アナリスト**: 投資戦略・リスク評価
- **研究者**: 論文執筆・データ分析

**特徴**：
- 推論時間は長い（30秒〜数分）が、高品質な分析
- 専門分野の制約が自動適用される
- 全推論過程が記録・検証可能

### ❌ 向いていない用途

- 単純な質問回答（ChatGPTで十分）
- 創作活動（小説、詩など）
- 雑談や娯楽目的
- 即座の回答が必要な場面

---

## 🔍 高度な活用方法

### 分野別制約の活用

CoreThink-MCPは以下の7分野を自動検出し、専門制約を適用します：

- **medical**: 医療安全・診断精度重視
- **legal**: 法的根拠・コンプライアンス重視
- **financial**: 金融規制・リスク管理重視
- **engineering**: 技術的妥当性・安全性重視
- **ai_ml**: AI/ML倫理・技術的正確性重視
- **cloud_devops**: インフラ安全・可用性重視
- **safety_critical**: 最高レベルの安全性要求

### 推論履歴の活用

```bash
# 推論過程の確認
cat logs/reasoning_history.md

# 特定パターンの検索
grep -E "(医療|診断)" logs/reasoning_history.md

# uv環境でのログ分析スクリプト実行
uv run python scripts/analyze_reasoning.py
```

### 機能カスタマイズ

```yaml
# conf/feature_flags.yaml
sampling_enabled: true      # LLM補完機能
history_enabled: true       # 推論履歴記録
adaptive_depth: true        # 推論深度自動調整
domain_detection: true      # 分野自動検出
```

### uvでの開発・テスト

```bash
# 依存関係の更新
uv add numpy pandas  # 新しいパッケージ追加
uv sync               # 依存関係同期

# テスト実行
uv run pytest tests/

# 開発サーバー起動
uv run python -m src.corethink_mcp.server.corethink_server --dev
```

---

## 📞 サポート・コミュニティ

### 質問・バグレポート

- **GitHub Issues**: [CoreThink-MCP Issues](https://github.com/kechirojp/CoreThink-MCP/issues)
- **技術文書**: [docs/](../docs/) フォルダ内の専門ガイド
- **論文参照**: [arXiv:2509.00971v2](https://arxiv.org/abs/2509.00971)

### 開発者向け情報

- **CONTRIBUTING.md**: 開発参加ガイド
- **技術仕様**: GSR 4層アーキテクチャ実装
- **拡張方法**: 新分野・制約の追加手順

---

## 🚀 次のステップ

1. **基本操作に慣れる**: 自分の専門分野での簡単な質問から開始
2. **推論過程を理解する**: `logs/reasoning_history.md` で推論の流れを確認
3. **高度な機能を試す**: 複雑な問題での多段階推論を体験
4. **専門制約をカスタマイズ**: 自分の業務に特化した制約の追加

CoreThink-MCPは「考える」プロセスを可視化し、信頼できるAI判断支援を提供します。時間をかけてでも「正しく考える」ことの価値を体験してください。
