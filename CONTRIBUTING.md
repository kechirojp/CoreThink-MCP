# 🤝 CoreThink-MCP コントリビューションガイド

CoreThink-MCP プロジェクトへの貢献を検討いただき、ありがとうございます！  
このガイドでは、効果的にプロジェクトに参加する方法を説明します。

## 🎯 プロジェクトのビジョン

**CoreThink-MCP** は、自然言語での推論（GSR）を通じて安全なコード変更を実現するMCPサーバーです。

### 核となる価値観

- **安全性第一**: すべての変更はサンドボックスで検証
- **自然言語中心**: 技術的でない人にも使いやすいインターフェース
- **実世界の適用**: 医療・法律・金融など専門分野での実用性
- **オープンソース**: 透明性と協力による継続的改善

---

## 🚀 参加方法

### 1. 簡単な参加方法

**👥 ユーザーとして参加**:
- バグ報告や機能要望を [Issues](https://github.com/kechirojp/CoreThink-MCP/issues) に投稿
- [Discussions](https://github.com/kechirojp/CoreThink-MCP/discussions) での質問や議論
- ドキュメントの改善提案

**📚 知識共有**:
- 使用事例の共有（どんな分野でどう使ったか）
- FAQ への質問追加
- チュートリアルや解説記事の投稿

### 2. 開発者として参加

**🔧 コード貢献**:
- バグ修正
- 新機能の実装
- パフォーマンス改善
- テストの追加

**📖 ドキュメント改善**:
- API ドキュメント
- ユーザーガイド
- 開発者向けドキュメント

---

## 📋 コントリビューションの種類

### 🐛 バグ報告

**良いバグ報告の例**:

```markdown
## 問題の概要
医療分野の分析時に「UnknownDomainError」が発生する

## 再現手順
1. Claude Desktop で CoreThink-MCP を起動
2. 「患者の診断レポートを分析してください」と入力
3. 以下のエラーが表示される

## 期待される動作
医療ドメインとして認識され、医療制約ルールで分析される

## 実際の動作
```
ERROR: Unknown domain detected for input: 患者の診断レポート
```

## 環境情報
- OS: Windows 11
- Python: 3.11.5
- CoreThink-MCP: v1.2.0
- Claude Desktop: 最新版

## 追加情報
診断ツール結果:
```bash
python tools/diagnostic.py --section keywords
```
```

### 💡 機能要望

**構造化された機能要望**:

```markdown
## 機能の概要
建設業界向けの安全管理制約ルールの追加

## 背景・モチベーション
建設現場では労働安全衛生法に基づく厳格な安全管理が必要だが、
現在のドメインでは十分にカバーされていない

## 提案する解決方法
1. `constraints_construction.txt` の作成
2. 建設業界特有のキーワード追加（重機、足場、安全帯など）
3. 労働安全衛生法に基づく制約ルール定義

## 代替案
既存の engineering ドメインを拡張する方法

## 追加情報
- 対象ユーザー: 建設会社、安全管理者
- 関連法規: 労働安全衛生法、建設業法
- 類似システム: 〇〇システムの安全チェック機能
```

### 🔧 コード改善

**プルリクエストの品質基準**:

1. **明確な目的**: 何を解決するのかを明記
2. **テスト追加**: 変更に対応するテストを含める
3. **ドキュメント更新**: 必要に応じてドキュメントも更新
4. **小さな変更**: 一度に多くを変更せず、段階的に

---

## 🛠 開発環境のセットアップ

### 前提条件

```bash
# Python 3.8以上
python --version

# Git
git --version

# (推奨) UV パッケージマネージャー
pip install uv
```

### 開発環境構築

```bash
# 1. リポジトリをフォーク・クローン
git clone https://github.com/YOUR_USERNAME/CoreThink-MCP.git
cd CoreThink-MCP

# 2. 開発ブランチを作成
git checkout -b feature/your-feature-name

# 3. 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. 依存関係をインストール
pip install -e .[dev]

# 5. 開発用追加パッケージ
pip install pytest black flake8 mypy

# 6. 診断ツールで環境確認
python tools/diagnostic.py
```

### 開発ワークフロー

```bash
# 1. 最新のmainブランチを取得
git checkout main
git pull upstream main

# 2. 新しい機能ブランチを作成
git checkout -b feature/add-construction-domain

# 3. 変更を実装
# ... コード編集 ...

# 4. テストを実行
pytest tests/
python tools/diagnostic.py --section keywords

# 5. コードフォーマット
black src/
flake8 src/

# 6. コミット
git add .
git commit -m "feat: 建設業界ドメインの制約ルールを追加

- constraints_construction.txt を新規作成
- 建設業界特有のキーワード28個を追加
- 労働安全衛生法に基づく制約ルール定義
- テストケースを追加

Closes #123"

# 7. プッシュしてプルリクエスト作成
git push origin feature/add-construction-domain
```

---

## 📝 コーディング規約

### Python コーディングスタイル

```python
# Good: 明確な関数名と型ヒント
def detect_construction_safety_issues(
    content: str, 
    safety_level: str = "standard"
) -> List[SafetyIssue]:
    """
    建設現場の安全性問題を検出
    
    Args:
        content: 分析対象のテキスト
        safety_level: 安全レベル ("basic", "standard", "strict")
        
    Returns:
        検出された安全性問題のリスト
        
    Raises:
        ValueError: 無効な safety_level が指定された場合
    """
    if safety_level not in ["basic", "standard", "strict"]:
        raise ValueError(f"Invalid safety_level: {safety_level}")
        
    # 実装...
    return detected_issues

# Bad: 不明瞭な関数名、型ヒントなし
def check(txt, lvl="std"):
    # 何をチェックするのか不明
    pass
```

### ドキュメント規約

```python
class ConstructionDomainDetector:
    """
    建設業界ドメイン検出器
    
    建設現場、安全管理、工事関連のテキストを検出し、
    適切な制約ルールを適用するためのドメイン分類を行う。
    
    Examples:
        >>> detector = ConstructionDomainDetector()
        >>> result = detector.detect("現場の安全確認をお願いします")
        >>> result.domain
        'construction'
        >>> result.confidence
        0.95
        
    Attributes:
        keywords: 建設業界キーワードリスト
        safety_rules: 安全管理ルール定義
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        検出器を初期化
        
        Args:
            config_path: 設定ファイルのパス（省略時はデフォルト）
        """
        pass
```

### テスト記述ガイドライン

```python
import pytest
from unittest.mock import Mock, patch

def test_construction_domain_detection_with_safety_keywords():
    """安全管理キーワードで建設ドメインが正しく検出されることを確認"""
    # Arrange
    detector = ConstructionDomainDetector()
    safety_text = "現場の安全帯着用確認と足場の点検をお願いします"
    
    # Act
    result = detector.detect(safety_text)
    
    # Assert
    assert result.domain == "construction"
    assert result.confidence > 0.8
    assert "安全帯" in result.matched_keywords
    assert "足場" in result.matched_keywords

def test_construction_domain_detection_with_ambiguous_text():
    """曖昧なテキストでの動作を確認"""
    detector = ConstructionDomainDetector()
    ambiguous_text = "プロジェクトの管理について"
    
    result = detector.detect(ambiguous_text)
    
    # 曖昧なケースでは general ドメインにフォールバック
    assert result.domain == "general"
    assert result.confidence < 0.5

@patch('corethink_mcp.server.core._load_domain_keywords')
def test_construction_domain_with_mocked_keywords(mock_load):
    """キーワード読み込みのモック化テスト"""
    # モックデータ設定
    mock_load.return_value = {
        'construction': ['建設', '現場', '安全', '工事']
    }
    
    detector = ConstructionDomainDetector()
    result = detector.detect("建設現場の安全管理")
    
    assert result.domain == "construction"
    mock_load.assert_called_once()
```

---

## 🔍 レビュープロセス

### プルリクエストチェックリスト

- [ ] **目的が明確**: PR の説明で何を解決するかが分かる
- [ ] **小さな変更**: 一度に大量の変更をせず、段階的に
- [ ] **テスト追加**: 新機能・修正にはテストを含める
- [ ] **ドキュメント更新**: 必要に応じてドキュメントも更新
- [ ] **型ヒント**: 新しい関数には型ヒントを追加
- [ ] **エラーハンドリング**: 適切な例外処理を含める
- [ ] **パフォーマンス**: 重い処理にはキャッシュや最適化を検討
- [ ] **後方互換性**: 既存のAPIを壊さない

### コードレビューの観点

**機能性**:
- コードが期待通りに動作するか
- エッジケースが適切に処理されているか
- エラーハンドリングが十分か

**保守性**:
- コードが読みやすく理解しやすいか
- 適切な抽象化が行われているか
- 重複が避けられているか

**パフォーマンス**:
- 不要な計算や処理がないか
- メモリ使用量は適切か
- キャッシュの活用は検討されているか

**セキュリティ**:
- 入力検証は十分か
- 機密情報の漏洩リスクはないか
- サンドボックス実行が適切に行われているか

---

## 🏗 アーキテクチャガイドライン

### ディレクトリ構造

```
src/corethink_mcp/
├── server/                 # MCPサーバー本体
│   ├── corethink_server.py # メインサーバー
│   ├── domain_detection.py # ドメイン検出ロジック
│   └── safety_validator.py # 安全性検証
├── constraints/            # 制約ルール定義
│   ├── constraints_medical.txt
│   ├── constraints_legal.txt
│   └── constraints_[domain].txt
├── tools/                  # ユーティリティツール
│   ├── reasoning.py        # 推論エンジン
│   ├── validation.py       # 検証ツール
│   └── execution.py        # 実行エンジン
└── utils/                  # 共通ユーティリティ
    ├── logging.py          # ログ管理
    ├── cache.py            # キャッシュ管理
    └── config.py           # 設定管理
```

### 設計原則

**1. 単一責任の原則（SRP）**:
```python
# Good: 各クラスが単一の責任を持つ
class DomainDetector:
    """ドメイン検出のみに責任を持つ"""
    def detect(self, text: str) -> DetectionResult:
        pass

class SafetyValidator:
    """安全性検証のみに責任を持つ"""
    def validate(self, operation: Operation) -> ValidationResult:
        pass

# Bad: 複数の責任を持つ
class SuperProcessor:
    """検出・検証・実行すべてを行う"""
    def process_everything(self, text: str) -> Any:
        # ドメイン検出
        # 安全性検証  
        # コード実行
        # ログ出力
        pass
```

**2. 依存性注入（DI）**:
```python
# Good: 依存性を外部から注入
class ReasoningEngine:
    def __init__(
        self, 
        detector: DomainDetector,
        validator: SafetyValidator,
        executor: CodeExecutor
    ):
        self.detector = detector
        self.validator = validator
        self.executor = executor

# Bad: 内部で依存関係を作成
class ReasoningEngine:
    def __init__(self):
        self.detector = DomainDetector()  # 強結合
        self.validator = SafetyValidator()  # テストが困難
```

**3. 失敗の明示的処理**:
```python
from typing import Union, Optional
from dataclasses import dataclass

@dataclass
class DetectionResult:
    domain: Optional[str]
    confidence: float
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.error is None

# Good: 失敗を型で表現
def detect_domain(text: str) -> DetectionResult:
    try:
        # 検出処理
        return DetectionResult(domain="medical", confidence=0.9)
    except Exception as e:
        return DetectionResult(domain=None, confidence=0.0, error=str(e))

# Bad: 例外に依存
def detect_domain(text: str) -> str:
    # エラー時に例外が発生（呼び出し側で処理が複雑）
    return domain
```

---

## 📚 ドキュメント貢献

### ドキュメントの種類

**1. ユーザー向けドキュメント**:
- `docs/USER_GUIDE.md`: 包括的な使用方法
- `docs/QUICKSTART.md`: 5分で始める方法
- `docs/FAQ.md`: よくある質問と解決方法

**2. 開発者向けドキュメント**:
- `docs/ARCHITECTURE.md`: システム設計
- `docs/API.md`: API リファレンス
- `docs/DEVELOPMENT.md`: 開発ガイド

**3. 業界特化ドキュメント**:
- `docs/medical/`: 医療業界向けガイド
- `docs/legal/`: 法律業界向けガイド
- `docs/finance/`: 金融業界向けガイド

### ドキュメント記述のベストプラクティス

**構造化された内容**:
```markdown
# 機能名

## 概要
何ができるのかを1-2文で説明

## 使用例
具体的な使用方法を示す

## パラメータ
入力パラメータの詳細

## 戻り値
出力の詳細

## 注意事項
制限事項や注意点

## 関連項目
関連する機能やドキュメントへのリンク
```

**実用的な例を含める**:
```markdown
## 医療分野での使用例

**診断支援**:
```
患者の症状：発熱、咳、息切れ
血液検査：白血球数上昇、CRP高値

この情報から考えられる診断と追加検査を提案してください。
```

**期待される出力**:
- 考えられる診断（肺炎、COVID-19など）
- 推奨される追加検査
- 緊急度の評価
```

---

## 🎖 コントリビューター認定

### 貢献レベル

**🌱 Contributor**:
- バグ報告・機能要望
- ドキュメント改善
- 議論への参加

**🌿 Regular Contributor**:
- 複数のプルリクエスト
- コードレビュー参加
- ユーザーサポート

**🌳 Core Contributor**:
- 重要機能の実装
- アーキテクチャ設計
- リリース管理

**🏆 Maintainer**:
- プロジェクト全体の方向性
- セキュリティ監督
- コミュニティ管理

### 認定特典

- **GitHub プロフィール**: プロジェクトへの貢献を表示
- **コミュニティ**: 開発者コミュニティへの参加権
- **早期アクセス**: 新機能の先行体験
- **技術相談**: Core Contributor による技術サポート

---

## 📞 サポート・コミュニケーション

### コミュニケーションチャネル

**GitHub Issues**: バグ報告・機能要望  
**GitHub Discussions**: 質問・議論・アイデア  
**Discord**: リアルタイム質問・雑談  
**メール**: プライベートな問い合わせ

### 質問のベストプラクティス

**良い質問の例**:
```markdown
## 質問の概要
医療ドメインで「薬物相互作用」のキーワードが認識されない

## 試したこと
1. diagnostic.py でキーワードチェック済み
2. constraints_medical.txt に "薬物相互作用" が含まれていることを確認
3. キャッシュクリア済み

## 期待する動作
「薬物相互作用の分析をお願いします」で医療ドメインとして検出される

## 環境情報
- OS: macOS 13.5
- Python: 3.11.5
- CoreThink-MCP: v1.2.1
```

---

## 🙏 謝辞

CoreThink-MCP は多くの貢献者によって支えられています：

- **Core Developers**: 基盤アーキテクチャの設計・実装
- **Domain Experts**: 医療・法律・金融分野の専門知識提供
- **Community Contributors**: バグ報告・機能改善・ドキュメント整備
- **Users**: 貴重なフィードバックと使用事例の共有

あなたの貢献も、このプロジェクトを次のレベルに押し上げる重要な一歩になります。

**一緒に、より安全で使いやすい推論システムを作りましょう！** 🚀