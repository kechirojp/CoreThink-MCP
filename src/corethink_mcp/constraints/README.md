# CoreThink-MCP 制約管理システム

このディレクトリには、CoreThink-MCPサーバーで使用される分野別制約ファイルが格納されています。

## 📂 ファイル構成

| ファイル名 | 説明 | 適用分野 |
|-----------|------|----------|
| `constraints.txt` | 基本制約（全分野共通） | 一般的な開発・推論制約 |
| `constraints_financial.txt` | 金融・融資制約 | 銀行・融資・FinTech・投資 |
| `constraints_ai_ml.txt` | AI・機械学習制約 | AI開発・機械学習・データサイエンス |
| `constraints_cloud_devops.txt` | クラウド・DevOps制約 | AWS・Azure・GCP・コンテナ・CI/CD |
| `constraints_medical.txt` | 医療分野制約 | 診断・治療・医療機器・薬事 |
| `constraints_legal.txt` | 法的制約 | 法務・契約・コンプライアンス |
| `constraints_safety_critical.txt` | 安全重要制約 | 航空・原子力・制御システム |
| `constraints_engineering.txt` | 工学制約 | エンジニアリング・建築・設計 |

## 🔄 自動適用システム

CoreThink-MCPサーバーは、ユーザーの要求内容から**自動的に**関連分野を検出し、適切な制約ファイルを適用します：

### 検出キーワード例

- **金融分野**: 融資、貸付、銀行、金利、投資、FinTech、暗号資産
- **AI分野**: 機械学習、LLM、Transformer、データサイエンス、ニューラルネット
- **医療分野**: 診断、症状、治療、薬物、患者、医師、臨床
- **法的分野**: 契約、法的、裁判、規制、コンプライアンス
- **クラウド分野**: AWS、Azure、Docker、Kubernetes、CI/CD
- **安全重要分野**: 航空、原子力、自動運転、制御システム

## 📝 制約ファイルの構造

各制約ファイルは以下の形式で記述されています：

```text
## カテゴリ名
MUST: 必須事項（違反禁止）
NEVER: 禁止事項（絶対実行不可）
SHOULD: 推奨事項（ベストプラクティス）
```

## 🛠 開発者向け情報

### 新しい分野の制約を追加する場合

1. `constraints_[分野名].txt` ファイルを作成
2. `corethink_server.py` の `_detect_domain()` 関数にキーワードを追加
3. 制約ファイルの内容を適切な形式で記述

### 制約の優先順位

1. 法的制約（MUST）> 倫理制約（SHOULD）> 推奨制約（RECOMMEND）
2. 緊急時制約 > 通常制約
3. 国際規制 > 国内規制（より厳格な方を適用）
4. 顧客保護 > 事業利益

---

## 📋 更新履歴

- 2025年9月12日: 制約ファイルを分野別に整理、constraintsフォルダを新設
- 2025年9月12日: 金融・融資制約ファイルを新規作成
- 2025年9月11日: 基本制約システム実装

## 🔗 関連ドキュメント

- [CoreThink-MCP README](../../../README.md)
- [詳細設計書](../../../CoreThink_MCP_統合GSR推論エンジン_詳細設計書_重要書類.md)
- [実装計画](../../../IMPLEMENTATION_PLAN.md)