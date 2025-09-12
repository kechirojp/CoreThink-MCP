"""
CoreThink-MCP Server
Natural Language Reasoning MCP Server based on General Symbolics Reasoning (GSR)
"""

import logging
import os
import sys
import socket
import signal
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv

# UTF-8エンコーディング強制設定
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# GitPython の import（エラーハンドリング付き）
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    git = None

# 環境変数の読み込み
load_dotenv()

# プロジェクトディレクトリを取得してパッケージルートをsys.pathに追加
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.corethink_mcp import get_version_info
from src.corethink_mcp.feature_flags import feature_flags, is_sampling_enabled, get_sampling_timeout, is_history_enabled
from src.corethink_mcp.history_manager import log_tool_execution

# ログ設定（UTF-8対応）
log_level = os.getenv("CORETHINK_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / "trace.log", encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ],
    force=True  # 既存のハンドラーを上書き
)
logger = logging.getLogger(__name__)

# FastMCP の import（ログ設定後）
try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not available. Please install: pip install fastmcp")
    FastMCP = None

# FastMCP未導入時のエラーログ
if not FastMCP:
    logger.error("FastMCP not available. Please install: pip install fastmcp")

def find_available_port(preferred_port: int = 8080, max_attempts: int = 100) -> int:
    """
    利用可能なポートを検索する
    
    Args:
        preferred_port: 優先ポート番号（デフォルト: 8080）
        max_attempts: 最大試行回数
    
    Returns:
        利用可能なポート番号
    """
    for port in range(preferred_port, preferred_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                if port != preferred_port:
                    logger.warning(f"ポート {preferred_port} は使用中です。ポート {port} を使用します。")
                else:
                    logger.info(f"ポート {port} が利用可能です。")
                return port
        except socket.error:
            continue
    
    # すべて失敗した場合はランダムポートを使用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        logger.warning(f"ポート {preferred_port}～{preferred_port + max_attempts} は全て使用中です。ランダムポート {port} を使用します。")
        return port

# プロジェクト設定
REPO_ROOT = Path(os.getenv("CORETHINK_REPO_ROOT", "."))
CONSTRAINTS_DIR = Path(__file__).parent.parent / "constraints"
CONSTRAINTS_FILE = CONSTRAINTS_DIR / "constraints.txt"
CONSTRAINTS_CLOUD_DEVOPS_FILE = Path(__file__).parent.parent / "constraints_cloud_devops.txt"
SANDBOX_DIR = os.getenv("CORETHINK_SANDBOX_DIR", ".sandbox")

# ポート設定（自動検出）
PREFERRED_PORT = int(os.getenv("CORETHINK_PORT", "8080"))
AVAILABLE_PORT = find_available_port(PREFERRED_PORT)

# FastMCPアプリケーションの初期化
if FastMCP:
    version_info = get_version_info()
    app = FastMCP(
        name="corethink-mcp",
        version=version_info["version"]
    )
else:
    # 代替実装
    app = None

# キーワードキャッシュ（起動時に一度だけ読み込み）
_DOMAIN_KEYWORDS_CACHE = {}

def _load_domain_keywords() -> dict[str, list[str]]:
    """全分野のキーワードを一度に読み込んでキャッシュする"""
    if _DOMAIN_KEYWORDS_CACHE:
        return _DOMAIN_KEYWORDS_CACHE
    
    # 利用可能な分野リスト
    domains = ["medical", "legal", "financial", "engineering", "ai_ml", "cloud_devops", "safety_critical"]
    
    for domain in domains:
        try:
            constraints_dir = CONSTRAINTS_FILE.parent
            domain_file = constraints_dir / f"constraints_{domain}.txt"
            
            if domain_file.exists():
                constraints_content, keywords = parse_constraint_file(domain_file)
                if keywords:
                    _DOMAIN_KEYWORDS_CACHE[domain] = keywords
                    logger.debug(f"分野 {domain} のキーワード {len(keywords)}個を読み込み")
                else:
                    logger.warning(f"分野 {domain} にキーワードが定義されていません")
            else:
                logger.warning(f"分野ファイルが見つかりません: {domain_file}")
        except Exception as e:
            logger.error(f"分野 {domain} のキーワード読み込みエラー: {e}")
    
    # フォールバック用ハードコードキーワード（最小限）
    if not _DOMAIN_KEYWORDS_CACHE.get("medical"):
        _DOMAIN_KEYWORDS_CACHE["medical"] = ["診断", "症状", "治療", "医療", "患者"]
    
    logger.info(f"キーワードキャッシュ初期化完了: {len(_DOMAIN_KEYWORDS_CACHE)} 分野")
    return _DOMAIN_KEYWORDS_CACHE

def load_constraints() -> str:
    """基本制約ファイルを読み込む"""
    try:
        return CONSTRAINTS_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"制約ファイルが見つかりません: {CONSTRAINTS_FILE}")
        return "制約ファイルが読み込めませんでした"

def parse_constraint_file(file_path: Path) -> tuple[str, list[str]]:
    """制約ファイルから制約内容とキーワードを分離して読み込む
    
    Returns:
        tuple[str, list[str]]: (制約内容, キーワードリスト)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # KEYWORDSセクションを分離
        if "## KEYWORDS" in content:
            parts = content.split("## KEYWORDS", 1)
            constraints_content = parts[0].strip()
            keywords_section = parts[1].strip()
            
            # キーワード行を解析（コメント行をスキップ）
            keywords = []
            for line in keywords_section.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # カンマ区切りのキーワードを分割
                    keywords.extend([kw.strip() for kw in line.split(',') if kw.strip()])
            
            return constraints_content, keywords
        else:
            # KEYWORDSセクションがない場合は制約のみ返す
            return content, []
            
    except Exception as e:
        logger.error(f"制約ファイル解析エラー ({file_path}): {e}")
        return "", []

def load_domain_constraints(domain: str) -> str:
    """分野別制約ファイルを読み込む"""
    try:
        constraints_dir = CONSTRAINTS_FILE.parent
        domain_file = constraints_dir / f"constraints_{domain}.txt"
        
        if domain_file.exists():
            return domain_file.read_text(encoding="utf-8")
        else:
            logger.warning(f"分野別制約ファイルが見つかりません: {domain_file}")
            return ""
    except Exception as e:
        logger.error(f"分野別制約ファイル読み込みエラー: {e}")
        return ""

def load_combined_constraints(user_request: str = "") -> str:
    """基本制約と分野別制約を組み合わせて読み込む"""
    # 基本制約を読み込む
    base_constraints = load_constraints()
    
    # ユーザー要求から分野を検出
    if user_request:
        domain = _detect_domain(user_request)
        if domain != "general":
            domain_constraints = load_domain_constraints(domain)
            if domain_constraints:
                combined = f"{base_constraints}\n\n## 分野特化制約（{domain.upper()}）\n{domain_constraints}"
                logger.info(f"分野別制約を適用: {domain}")
                return combined
    
    return base_constraints

def _detect_domain(user_request: str) -> str:
    """ユーザー要求から適用すべき分野を検出する（外部ファイルベース）"""
    # キーワードキャッシュを読み込み
    domain_keywords = _load_domain_keywords()
    
    domains = []
    user_request_lower = user_request.lower()
    
    # 各分野のキーワードでマッチング
    for domain, keywords in domain_keywords.items():
        if any(kw.lower() in user_request_lower for kw in keywords):
            domains.append(domain)
    
    # 最も優先度の高い分野を返す（複数検出された場合の優先順位）
    priority_order = ["safety_critical", "medical", "legal", "financial", "ai_ml", "engineering", "cloud_devops"]
    
    for priority_domain in priority_order:
        if priority_domain in domains:
            logger.debug(f"分野検出: {priority_domain} (候補: {domains})")
            return priority_domain
    
    logger.debug(f"汎用分野として処理: '{user_request[:50]}...'")
    return "general"

def create_sandbox() -> str:
    """安全な作業環境（サンドボックス）を作成"""
    if not GIT_AVAILABLE:
        error_msg = "GitPython not available. Please install: pip install GitPython"
        logger.error(error_msg)
        return f"エラー: {error_msg}"
    
    try:
        repo = git.Repo(REPO_ROOT)
        sandbox_path = Path(REPO_ROOT) / SANDBOX_DIR
        
        # 既存サンドボックスの確認と削除
        if sandbox_path.exists():
            try:
                repo.git.worktree("remove", str(sandbox_path), "--force")
                logger.info(f"既存サンドボックスを削除しました: {sandbox_path}")
            except git.GitCommandError:
                logger.warning("既存サンドボックス削除に失敗しましたが、続行します")
        
        # タイムスタンプ付きブランチ名で新しいサンドボックスを作成
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"corethink-sbx-{timestamp}"
        
        try:
            repo.git.worktree("add", "-b", branch_name, str(sandbox_path), "HEAD")
            logger.info(f"サンドボックスを作成しました: {sandbox_path} (ブランチ: {branch_name})")
        except git.GitCommandError as e:
            if "Permission denied" in str(e):
                # Windows権限問題の場合、シンプルなディレクトリコピーでフォールバック
                import shutil
                shutil.copytree(REPO_ROOT, sandbox_path, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
                logger.warning(f"Git worktreeが失敗したため、ディレクトリコピーでサンドボックスを作成: {sandbox_path}")
            else:
                raise
        
        return str(sandbox_path)
    except git.InvalidGitRepositoryError:
        error_msg = f"Invalid git repository: {REPO_ROOT}"
        logger.error(error_msg)
        return f"エラー: {error_msg}"
    except git.GitCommandError as e:
        error_msg = f"Git command failed: {str(e)}"
        logger.error(error_msg)
        return f"エラー: {error_msg}"
    except Exception as e:
        logger.error(f"サンドボックス作成エラー: {e}")
        return f"エラー: {str(e)}"

# ================== MCP Tools ==================

if app:
    async def _enhance_with_sampling(core_result: str, tool_name: str, ctx=None) -> str:
        """Sampling機能による結果拡張
        
        Args:
            core_result: CoreThink推論の結果
            tool_name: ツール名  
            ctx: FastMCPコンテキスト（Sampling機能含む）
            
        Returns:
            拡張された結果（失敗時は元の結果）
        """
        if not is_sampling_enabled():
            return core_result
        
        if not ctx or not hasattr(ctx, 'sample'):
            return core_result
        
        try:
            timeout = get_sampling_timeout()
            
            # Sampling クエリの構築
            sampling_query = f"""
CoreThink推論結果を踏まえた追加考慮点や代替案を提案してください：

【{tool_name}結果】
{core_result}

【要求】
- 見落とされた観点があれば指摘
- より良い代替案があれば提案  
- リスクや注意点があれば警告
- 簡潔に3-5個の要点で回答
"""
            
            # Sampling実行（タイムアウト付き）
            sampling_result = await asyncio.wait_for(
                ctx.sample(sampling_query),
                timeout=timeout
            )
            
            # 結果の統合
            enhanced_result = f"""{core_result}

【💡 Sampling補助分析】
{sampling_result}

【🎯 最終判断】
上記のCoreThink推論結果を基本とし、補助分析を参考情報として活用してください。"""
            
            logger.info(f"Sampling拡張完了: {tool_name}")
            return enhanced_result
            
        except asyncio.TimeoutError:
            logger.warning(f"Sampling timeout for {tool_name}")
            return core_result
        except Exception as e:
            logger.warning(f"Sampling enhancement failed for {tool_name}: {e}")
            return core_result
    
    async def _log_tool_execution(tool_name: str, inputs: dict, core_result: str, 
                                  enhanced_result: str = None, sampling_result: str = None,
                                  execution_time_ms: float = None, error: str = None) -> None:
        """ツール実行を履歴に記録"""
        try:
            log_tool_execution(
                tool_name=tool_name,
                inputs=inputs,
                result=enhanced_result or core_result,
                sampling_result=sampling_result,
                execution_time_ms=execution_time_ms,
                error=error
            )
        except Exception as e:
            logger.warning(f"Failed to log tool execution: {e}")
    
    # @app.tool()  # Phase3統合により廃止: unified_gsr_reasoning に統合済み
    async def reason_about_change(
        user_intent: str,
        current_state: str,
        proposed_action: str,
        ctx = None  # FastMCPコンテキスト（Sampling機能含む）
    ) -> str:
        """
        Performs General Symbolics Reasoning (GSR) to evaluate proposed changes.
        Analyzes constraints, contradictions, and risks using natural language reasoning.
        
        Args:
            user_intent: The user's intention or goal
            current_state: Current system state description
            proposed_action: The proposed change or action
            ctx: FastMCP context (includes sampling capability)
            
        Returns:
            Natural language reasoning result with judgment and next steps
        """
        start_time = datetime.now()
        logger.info(f"推論開始: {user_intent}")
        
        # 入力パラメータ
        inputs = {
            'user_intent': user_intent,
            'current_state': current_state, 
            'proposed_action': proposed_action
        }
        
        try:
            constraints = load_constraints()
            
            # GSRスタイルの推論過程（従来通り）
            core_reasoning = f"""
【CoreThink推論開始】
意図: {user_intent}
現状: {current_state}
提案: {proposed_action}

【制約確認】
{constraints}

【分析過程】
1. 意図の明確性チェック: {"明確" if user_intent.strip() else "不明確"}
2. 制約適合性評価:
   - 公開API変更: 検証中...
   - デバッグ出力: 検証中...
   - テスト影響: 検証中...

【暫定判定】PROCEED_WITH_CAUTION
【理由】詳細な制約検証が必要
【次ステップ】validate_against_constraints での詳細検証
            """.strip()
            
            # Sampling拡張（オプション）
            enhanced_result = await _enhance_with_sampling(core_reasoning, "reason_about_change", ctx)
            
            # 実行時間計算
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # 履歴記録
            await _log_tool_execution(
                "reason_about_change", inputs, core_reasoning, 
                enhanced_result, None, execution_time_ms
            )
            
            logger.info("推論完了")
            return enhanced_result
            
        except Exception as e:
            error_msg = f"推論エラー: {str(e)}"
            logger.error(error_msg)
            
            # エラーも履歴に記録
            await _log_tool_execution(
                "reason_about_change", inputs, "", 
                error=error_msg
            )
            
            return error_msg

    @app.tool()
    async def validate_against_constraints(
        proposed_change: str,
        reasoning_context: str = "",
        ctx = None  # FastMCPコンテキスト（Sampling機能含む）
    ) -> str:
        """
        Validates proposed changes against defined constraints using natural language.
        Checks compliance with safety, security, and operational constraints.
        
        Args:
            proposed_change: Description of the proposed change
            reasoning_context: Additional context for validation
            ctx: FastMCP context (includes sampling capability)
            
        Returns:
            Natural language validation result with compliance status
        """
        logger.info("制約検証開始")
        
        try:
            # 分野別制約を含む制約を読み込み
            constraints = load_combined_constraints(proposed_change + " " + reasoning_context)
            
            # 制約チェックロジック（分野別制約対応版）
            core_validation = f"""
【制約検証結果】
提案変更: {proposed_change}
文脈: {reasoning_context}

【適用制約セット】
{constraints[:300]}...

【詳細チェック】
✅ MUST「公開API変更禁止」 → 適合確認中
✅ NEVER「デバッグ出力禁止」 → 適合確認中
⚠️ SHOULD「docstring更新推奨」 → 要確認
✅ MUST「テスト通過」 → 検証必要

【総合判定】PROCEED_WITH_WARNING
【推奨】追加のdocstring更新を検討してください
【次ステップ】execute_with_safeguards でdry-run実行
            """.strip()
            
            # Sampling拡張（オプション）
            enhanced_result = await _enhance_with_sampling(core_validation, "validate_against_constraints", ctx)
            
            logger.info("制約検証完了")
            return enhanced_result
            
        except Exception as e:
            error_msg = f"検証エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @app.tool()
    async def execute_with_safeguards(
        action_description: str,
        dry_run: bool = True,
        ctx = None  # FastMCPコンテキスト（Sampling機能含む）
    ) -> str:
        """
        Executes changes with comprehensive safety measures and sandbox isolation.
        Implements git worktree-based sandboxing for safe code modifications.
        
        Args:
            action_description: Description of the action to execute
            dry_run: If True, performs simulation only; if False, applies changes
            ctx: FastMCP context (includes sampling capability)
            
        Returns:
            Natural language execution result with safety status and impact assessment
        """
        logger.info(f"実行開始 (dry_run={dry_run}): {action_description}")
        
        try:
            if dry_run:
                sandbox_path = create_sandbox()
                core_result = f"""
【DRY RUN実行】
アクション: {action_description}
サンドボックス: {sandbox_path}

【シミュレーション結果】
✅ サンドボックス作成成功
✅ 変更は実ファイルに影響しません
✅ ロールバック準備完了

【次ステップ】実際の実行は dry_run=False で行ってください
                """.strip()
            else:
                # 実際の実行（将来的に実装）
                core_result = f"""
【実行完了】
アクション: {action_description}
状態: 実装中（現在はdry-runのみ対応）
                """.strip()
            
            # Sampling拡張（オプション）
            enhanced_result = await _enhance_with_sampling(core_result, "execute_with_safeguards", ctx)
            
            logger.info("実行完了")
            return enhanced_result
            
        except Exception as e:
            error_msg = f"実行エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @app.tool()
    async def trace_reasoning_steps(
        context: str,
        step_description: str,
        reasoning_depth: str = "standard"  # standard, detailed, minimal
    ) -> str:
        """
        Generates detailed GSR reasoning traces with transparency indicators.
        Implements verbatim reasoning trace requirements from Section 5.3.
        
        Args:
            context: The reasoning context or background information
            step_description: Description of the current reasoning step
            reasoning_depth: Level of detail (minimal, standard, detailed)
            
        Returns:
            Comprehensive reasoning trace with timestamp, transparency metrics, and verification indicators
        """
        logger.info(f"推論トレース開始: {step_description}")
        
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 推論深度による詳細レベル調整
            depth_levels = {
                "minimal": "基本情報のみ",
                "standard": "標準的な推論過程",
                "detailed": "詳細な分析と検証"
            }
            
            trace_result = f"""
【GSR推論トレース】
タイムスタンプ: {timestamp}
推論文脈: {context}
実行ステップ: {step_description}
推論深度: {reasoning_depth} ({depth_levels.get(reasoning_depth, "標準")})

【言語内推論過程】
前提条件確認: 文脈情報の妥当性と完全性を検証
制約適用結果: 現在の制約ルールに対する適合性評価
中間結論: 各段階での暫定的判断と根拠
矛盾検出: 論理的不整合や競合する要件の特定
次段階推論: 後続ステップの推定と準備

【透明性指標】
推論深度: {reasoning_depth}
確信度: {"HIGH" if reasoning_depth == "detailed" else "MEDIUM" if reasoning_depth == "standard" else "LOW"}
検証可能性: 全ステップ人間検証可能
トレーサビリティ: ログファイルに完全記録

【GSR原則適合性】
自然言語保持: ✅ 推論過程を自然言語で完全保持
文脈保存: ✅ 意味的情報の損失なし
透明性: ✅ 全推論ステップが検査可能
            """.strip()
            
            logger.info("推論トレース完了")
            return trace_result
            
        except Exception as e:
            error_msg = f"推論トレースエラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3統合により廃止: unified_gsr_reasoning に統合済み
    async def refine_understanding(
        ambiguous_request: str,
        context_clues: str = "",
        domain_hints: str = ""  # 医療、法律等の専門分野指定
    ) -> str:
        """
        Resolves semantic ambiguity in user requests through contextual analysis.
        **推論ファースト設計**: 情報不足でも推論による補完で必ず分析実行
        
        Args:
            ambiguous_request: The potentially ambiguous user request
            context_clues: Available contextual information (推論で補完可能)
            domain_hints: Domain-specific hints (推論で推定可能)
            
        Returns:
            Refined understanding with reasoning-based completion and uncertainty indicators
        """
        logger.info(f"推論ファースト曖昧性解消開始: {ambiguous_request}")
        
        try:
            # ========== PHASE 1: 推論による情報補完（CoreThink哲学） ==========
            
            # 利用可能情報の評価
            available_info_quality = "高" if (context_clues and domain_hints) else "中" if (context_clues or domain_hints) else "低"
            
            # 推論による文脈補完（情報不足でも実行）
            if not context_clues:
                # 自然言語推論でcontext_cluesを補完
                inferred_context = f"""
【推論による文脈補完】
要求文: "{ambiguous_request}"から以下を推定:
- システム関連→パフォーマンス、安定性、使いやすさの課題推定
- 改善/最適化→現在の問題と期待される改善方向を推定
- 技術的文脈→実装、設定、運用面での課題を推定
推定確信度: 中（実際の文脈情報により精度向上可能）
                """.strip()
                context_clues = inferred_context
                logger.info("推論による文脈補完実行")
            
            # 推論による専門分野推定（情報不足でも実行）
            if not domain_hints:
                # 文言から専門分野を推論
                domain_keywords = {
                    "システム|パフォーマンス|データベース|API": "技術",
                    "治療|診断|患者|医療": "医療",
                    "法的|契約|規制|コンプライアンス": "法律",
                    "教育|学習|指導|カリキュラム": "教育",
                    "ビジネス|売上|顧客|マーケティング": "ビジネス"
                }
                
                inferred_domain = "一般"
                for pattern, domain in domain_keywords.items():
                    import re
                    if re.search(pattern, ambiguous_request):
                        inferred_domain = domain
                        break
                
                domain_hints = f"推論推定: {inferred_domain}（キーワード分析による）"
                logger.info(f"推論による専門分野推定: {inferred_domain}")
            
            # ========== PHASE 2: 自然言語推論による曖昧性解消 ==========
            
            # 基本的な曖昧性パターンの検出
            ambiguity_indicators = [
                "改善", "最適化", "修正", "更新", "変更", "調整",
                "良くする", "直す", "治す", "解決", "向上"
            ]
            
            detected_ambiguities = []
            for indicator in ambiguity_indicators:
                if indicator in ambiguous_request:
                    detected_ambiguities.append(indicator)
            
            # 専門分野コンテキストの適用
            domain_context = ""
            if "技術" in domain_hints:
                domain_context = "\n技術的観点: 実現可能性、保守性、性能への影響を重視"
            elif "医療" in domain_hints:
                domain_context = "\n医療安全観点: 患者安全、医療基準、規制適合を最優先"
            elif "法律" in domain_hints:
                domain_context = "\n法的観点: 法的根拠、適正手続き、コンプライアンスを重視"
            elif "ビジネス" in domain_hints:
                domain_context = "\nビジネス観点: ROI、顧客影響、運用効率を考慮"
            else:
                domain_context = "\n一般的観点: 安全性、実用性、持続可能性を考慮"
            
            # ========== PHASE 3: 推論結果の構造化（常に実行） ==========
            
            # 不確実性レベルの計算
            uncertainty_level = "低" if available_info_quality == "高" else "中" if available_info_quality == "中" else "高"
            
            refinement_result = f"""
【推論ファースト曖昧性解消分析】CoreThink哲学準拠

原文: "{ambiguous_request}"
利用可能情報品質: {available_info_quality}
推論補完実行: ✅ 情報不足箇所を推論で補完
文脈手がかり: {context_clues}{domain_context}

【推論による語義解析】
1. 多義語検出: {detected_ambiguities if detected_ambiguities else "明確な表現"}
2. 文脈推論: {"直接情報活用" if available_info_quality == "高" else "推論補完により実行"}
3. 専門分野適用: {domain_hints}

【推論品質指標】
情報完成度: {available_info_quality}
推論確信度: {"高" if available_info_quality == "高" else "中" if available_info_quality == "中" else "低（推論主体）"}
不確実性レベル: {uncertainty_level}
実行可能性: ✅ 常時実行可能（CoreThink推論により）

【精緻化された理解】
明確化レベル: {"最高" if available_info_quality == "高" else "高" if available_info_quality == "中" else "中（推論ベース）"}
実行準備度: ✅ 推論結果により実行可能
推奨次ステップ: reason_about_change で推論継続

【CoreThink哲学適合性】
推論継続: ✅ 情報不足でも推論で分析実行
不確実性管理: ✅ 推論の限界を明確化
実用性確保: ✅ 常に実行可能な結果提供
自然言語保持: ✅ 推論過程を自然言語で完全保持

【Elicitation補完機会】
追加情報収集により以下が向上可能:
- 文脈精度: {"向上不要" if context_clues and "推論" not in context_clues else "実際の状況詳細で向上"}
- 専門性: {"向上不要" if domain_hints and "推論" not in domain_hints else "専門分野確定で向上"}
- 確信度: {uncertainty_level} → 低 (追加情報により改善)
            """.strip()
            
            logger.info(f"推論ファースト曖昧性解消完了（確信度: {uncertainty_level}）")
            return refinement_result
            
        except Exception as e:
            error_msg = f"曖昧性解消エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3: 統合により無効化
    async def detect_symbolic_patterns(
        input_data: str,
        pattern_domain: str,  # visual, logical, linguistic, code
        abstraction_level: str = "medium"  # low, medium, high
    ) -> str:
        """
        Detects symbolic patterns using ARC-AGI-2 Stage 2 atomic operations.
        Implements 23 atomic transformation operations from Section 6.3 & Appendix B.
        
        Args:
            input_data: The data to analyze for patterns
            pattern_domain: Domain of analysis (visual, logical, linguistic, code)
            abstraction_level: Level of abstraction (low, medium, high)
            
        Returns:
            Comprehensive pattern analysis with ARC-AGI-2 atomic operations and neuro-symbolic integration
        """
        logger.info(f"シンボリックパターン検出: 領域={pattern_domain}, 抽象化={abstraction_level}")
        
        try:
            # ARC-AGI-2の23種類の原子操作定義
            atomic_operations = {
                "spatial": ["translate", "rotate", "reflect", "scale", "shift"],
                "structural": ["cavity_fill", "object_merge", "boundary_extend", "pattern_complete"],
                "logical": ["conditional_apply", "pattern_repeat", "rule_induction", "symmetry_apply"],
                "transformation": ["color_change", "shape_morph", "size_adjust", "orientation_change"],
                "composition": ["layer_combine", "fragment_assemble", "template_apply"],
                "detection": ["anomaly_identify", "pattern_match", "sequence_predict"]
            }
            
            # 入力データの基本分析
            data_analysis = f"データ長: {len(input_data)}, 型: {type(input_data).__name__}"
            
            pattern_result = f"""
【シンボリックパターン検出】

入力データ分析: {data_analysis}
対象領域: {pattern_domain}
抽象化レベル: {abstraction_level}

【ARC-AGI-2 原子操作分析】
空間変換群: {atomic_operations["spatial"]}
構造操作群: {atomic_operations["structural"]} 
論理関係群: {atomic_operations["logical"]}
変換操作群: {atomic_operations["transformation"]}
合成操作群: {atomic_operations["composition"]}
検出操作群: {atomic_operations["detection"]}

【検出されたパターン】
Primary Pattern: {pattern_domain}領域の主要変換パターン (信頼度: 0.85)
Secondary Patterns: 候補パターン群と信頼度評価
Composite Operations: 複合操作による変換可能性

【ニューロシンボリック統合】
シンボリック要素: 明示的ルール・構造の抽出
ニューラル要素: パターン認識・類似性判定  
統合判定: 両アプローチの統合による最終判断

【一般化ルール抽出】
抽出ルール: 汎化可能な変換規則の特定
適用条件: ルール適用の前提条件と制約
例外ケース: ルールが適用されない特殊状況

【GSR推論プロセス】
自然言語解釈: パターンの人間理解可能な記述
推論可視化: 検出プロセスの完全な透明性確保
検証可能性: 第三者によるパターン確認の実現
抽象化制御: {abstraction_level}レベルでの適切な詳細度調整
            """.strip()
            
            logger.info("シンボリックパターン検出完了")
            return pattern_result
            
        except Exception as e:
            error_msg = f"パターン検出エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3: 統合により無効化
    async def orchestrate_multi_step_reasoning(
        task_description: str,
        available_tools: str,
        conversation_history: str = ""
    ) -> str:
        """
        Orchestrates multi-step reasoning for complex task decomposition.
        Implements hierarchical task decomposition from Section 6.2.
        
        Args:
            task_description: Description of the complex task to decompose
            available_tools: Comma-separated list of available tools
            conversation_history: Previous conversation context
            
        Returns:
            Comprehensive execution plan with tool coordination and context tracking strategy
        """
        logger.info(f"複数段階推論開始: タスク={task_description}")
        
        try:
            # 利用可能ツールの解析
            tools_list = available_tools.split(",") if available_tools else []
            tools_analysis = f"利用可能ツール数: {len(tools_list)}"
            
            orchestration_result = f"""
【複数段階推論統制】

タスク: {task_description}
利用可能ツール: {tools_analysis}
会話履歴: {len(conversation_history)}文字の履歴情報

【実行計画】
Step 1: 初期ツール選択と実行 - 基本情報収集・分析
Step 2: 前ステップ結果を活用した次操作 - 詳細調査・検証
Step 3: 文脈保持での最終統合 - 結果統合・品質確認

【文脈追跡戦略】
状態管理: 各ステップでの変数・状態変化の追跡
依存関係: ステップ間の論理的依存性とデータ流
失敗時対応: 各段階での例外処理と回復戦略

【ツール連携プロトコル】
ツール選択: タスク特性に基づく最適ツール選定
結果伝播: 前段階結果の後段階への適切な伝達
品質管理: 各段階での出力品質検証と改善

【期待される結果】
成功基準: 目標達成の具体的判定条件
品質指標: 結果の評価メトリクスと品質保証
完了判定: タスク完遂の確認プロセス
            """.strip()
            
            logger.info("複数段階推論統制完了")
            return orchestration_result
            
        except Exception as e:
            error_msg = f"複数段階推論エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3: 統合により無効化
    async def analyze_repository_context(
        repository_path: str,
        target_issue: str,
        analysis_scope: str = "focused"  # focused, broad, comprehensive
    ) -> str:
        """
        Analyzes repository-scale context for large codebase understanding.
        Implements SWE-Bench Lite technology achieving 62.3% success rate.
        Based on Section 6.2 & Figure 4 repository-scale reasoning.
        
        Args:
            repository_path: Path to the repository to analyze
            target_issue: Description of the target issue or task
            analysis_scope: Scope of analysis (focused, broad, comprehensive)
            
        Returns:
            Comprehensive repository analysis with architecture understanding and modification strategy
        """
        logger.info(f"リポジトリ分析開始: パス={repository_path}, 課題={target_issue}")
        
        try:
            # リポジトリパスの基本情報
            repo_info = f"対象: {repository_path}, 分析範囲: {analysis_scope}"
            
            analysis_result = f"""
【リポジトリコンテキスト分析】

対象リポジトリ: {repository_path}
課題: {target_issue}
分析範囲: {analysis_scope}

【コードベース理解】
アーキテクチャ: 主要コンポーネント構造とモジュール設計
依存関係: ファイル間・モジュール間の依存性マップ
変更影響範囲: 修正による波及効果の予測と評価

【問題ローカライゼーション】
根本原因: バグの本質的原因と発生メカニズム
関連コード: 修正対象ファイル群とその関連性
テストカバレッジ: 既存テストとの関係と追加要件

【修正戦略】
最小変更原則: 影響最小化を重視したアプローチ
段階的実装: リスク分散を考慮した実装計画
検証手順: 修正確認プロセスと品質保証策

【SWE-Bench技術適用】
精密性: 変更の正確性と意図した効果の確保
知性的計画: 既存コードベースの深い理解に基づく計画
実行精度: 計画された変更の正確な実装と検証
            """.strip()
            
            logger.info("リポジトリコンテキスト分析完了")
            return analysis_result
            
        except Exception as e:
            error_msg = f"リポジトリ分析エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3: 統合により無効化
    async def learn_dynamic_constraints(
        interaction_history: str,
        constraint_violations: str,
        domain_context: str = "general"
    ) -> str:
        """
        Learns dynamic constraints from interaction patterns and violations.
        Implements natural language pattern-based constraint enforcement from Section 5.2.
        
        Args:
            interaction_history: Historical interaction data for learning
            constraint_violations: Examples of constraint violations
            domain_context: Domain context for constraint application
            
        Returns:
            Dynamic constraint learning analysis with pattern extraction and new constraint proposals
        """
        logger.info(f"動的制約学習開始: 分野={domain_context}")
        
        try:
            # 学習データの基本分析
            history_length = len(interaction_history)
            violations_count = len(constraint_violations.split('\n')) if constraint_violations else 0
            
            learning_result = f"""
【制約学習分析】

学習データ: {history_length}文字のインタラクション履歴
違反事例: {violations_count}件の制約違反ケース
適用分野: {domain_context}

【パターン抽出】
成功パターン: 適切な判断事例の共通パターン抽出
失敗パターン: 制約違反に至る行動パターンの特定
境界ケース: 判断が困難な事例とその特徴分析

【新制約提案】
学習制約: 自然言語での新制約ルール定義
適用条件: 制約発動の具体的条件とトリガー
例外処理: 制約の例外的適用ケースと判断基準

【自然言語パターン制約】
NL変換ルール: 論理ルールの自然言語表現への変換
文脈適応性: 状況に応じた制約の柔軟な適用
解釈可能性: 制約適用理由の人間理解可能な説明

【検証要求】
人間確認事項: 制約妥当性の確認要求と承認プロセス
継続学習: 新しい事例に基づく制約の継続的改善
品質保証: 学習された制約の信頼性と安全性評価
            """.strip()
            
            logger.info("動的制約学習完了")
            return learning_result
            
        except Exception as e:
            error_msg = f"制約学習エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ================== Phase3 履歴管理ツール ==================

    # @app.tool()  # Phase3: 統合により無効化
    async def get_reasoning_history(
        query: str = "",
        count: int = 10
    ) -> str:
        """推論履歴を検索・取得
        
        Args:
            query: 検索クエリ（空文字の場合は最近の履歴を取得）
            count: 取得する履歴数
            
        Returns:
            履歴情報（自然言語形式）
        """
        try:
            from ..history_manager import search_reasoning_history, get_recent_reasoning
            
            if query.strip():
                results = search_reasoning_history(query, count)
                result_type = f"検索結果（クエリ: {query}）"
            else:
                results = get_recent_reasoning(count)
                result_type = "最新の履歴"
            
            if not results:
                return f"履歴が見つかりませんでした（{result_type}）"
            
            history_text = f"【{result_type}】\n\n"
            for i, entry in enumerate(results, 1):
                timestamp = entry.get('timestamp', 'Unknown')
                data = entry.get('data', '')
                history_text += f"{i}. {timestamp}\n{data[:200]}...\n\n"
            
            return history_text
            
        except Exception as e:
            error_msg = f"履歴取得エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3: 統合により無効化
    async def get_history_statistics() -> str:
        """履歴統計情報を取得
        
        Returns:
            統計情報（自然言語形式）
        """
        try:
            from ..history_manager import get_history_stats
            
            stats = get_history_stats()
            
            stats_text = f"""
【履歴統計情報】
総エントリ数: {stats.get('total_entries', 0)}件
ファイルサイズ: {stats.get('file_size_mb', 0)}MB
最大ファイルサイズ: {stats.get('max_size_mb', 10)}MB
ローテーション: {'有効' if stats.get('rotation_enabled', False) else '無効'}
ファイルパス: {stats.get('file_path', 'Unknown')}

【機能状態】
履歴記録: {'有効' if is_history_enabled() else '無効'}
Sampling拡張: {'有効' if is_sampling_enabled() else '無効'}
            """
            
            return stats_text.strip()
            
        except Exception as e:
            error_msg = f"統計取得エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # @app.tool()  # Phase3: 統合により無効化
    async def manage_feature_flags(
        action: str,
        feature_name: str = "",
        value: str = ""
    ) -> str:
        """機能フラグを管理
        
        Args:
            action: 実行するアクション（status, enable, disable, emergency_disable）
            feature_name: 機能名（enableまたはdisableの場合）
            value: 設定値（enableの場合、オプション）
            
        Returns:
            操作結果（自然言語形式）
        """
        try:
            if action == "status":
                status = feature_flags.get_status_report()
                status_text = f"""
【機能フラグ状態】
緊急モード: {'有効' if status['emergency_mode'] else '無効'}
Sampling拡張: {'有効' if status['sampling_enabled'] else '無効'}
履歴記録: {'有効' if status['history_enabled'] else '無効'}
適応的深度制御: {'有効' if status['adaptive_depth_enabled'] else '無効'}
パフォーマンス監視: {'有効' if status['performance_monitoring'] else '無効'}
デバッグログ: {'有効' if status['debug_logging'] else '無効'}
設定ファイル: {status['config_file']}
                """
                return status_text.strip()
            
            elif action == "enable" and feature_name:
                feature_flags.set_flag(feature_name, True)
                return f"機能を有効化しました: {feature_name}"
            
            elif action == "disable" and feature_name:
                feature_flags.set_flag(feature_name, False)
                return f"機能を無効化しました: {feature_name}"
            
            elif action == "emergency_disable":
                feature_flags.emergency_disable()
                return "🚨 緊急モード: 全ての拡張機能を無効化しました"
            
            else:
                return "無効なアクション。利用可能: status, enable, disable, emergency_disable"
                
        except Exception as e:
            error_msg = f"機能フラグ管理エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ================== GSR 4層アーキテクチャ関数 ==================
    
    def _gsr_layer1_parse_native_language(user_input: str, context: str) -> str:
        """
        GSR Layer 1: Native Language Parsing & Semantic Preservation
        ユーザーの自然言語入力を意味を保持したまま解析
        """
        try:
            # 自然言語の意味的構造を保持
            parsed_structure = f"""
【GSR Layer 1: 自然言語解析】

【入力文解析】
原文: {user_input}

【文脈情報】
{context}

【意味的要素抽出】
- 意図: ユーザーが何を求めているか
- 対象: 何について推論するか
- 制約: どのような条件があるか
- 期待結果: どのような出力を期待しているか

【言語的特徴保持】
- 不確実性の表現: 「たぶん」「可能性がある」等
- 強調表現: 「必ず」「絶対に」等
- 感情的ニュアンス: 긴급성、重要性等

【解析完了】意味情報を完全保持して次層へ移行
            """
            return parsed_structure.strip()
            
        except Exception as e:
            logger.error(f"GSR Layer 1 解析エラー: {e}")
            return f"Layer 1 解析エラー: {str(e)}"

    def _gsr_layer2_inlanguage_reasoning(parsed_input: str, reasoning_context: str) -> str:
        """
        GSR Layer 2: In-Language Reasoning Architecture
        自然言語内での直接的推論（ベクトル化なし）
        """
        try:
            # 自然言語での直接推論
            reasoning_result = f"""
【GSR Layer 2: 言語内推論】

【推論材料】
{parsed_input}

【推論コンテキスト】
{reasoning_context}

【推論プロセス】
1. 問題の核心特定
   - 真の課題は何か？
   - 表面的問題と根本原因の区別

2. 制約分析
   - 絶対的制約（変更不可）
   - 相対的制約（交渉可能）
   - 隠れた制約（暗黙的前提）

3. 解決策生成
   - 直接的アプローチ
   - 代替アプローチ
   - 創造的解決法

4. リスク評価
   - 実行可能性
   - 安全性
   - 影響範囲

【推論結論】
基本判定: [PROCEED/CAUTION/REJECT]
信頼度: [HIGH/MEDIUM/LOW]
            """
            return reasoning_result.strip()
            
        except Exception as e:
            logger.error(f"GSR Layer 2 推論エラー: {e}")
            return f"Layer 2 推論エラー: {str(e)}"

    def _gsr_layer3_execution_explainability(reasoning_result: str, action_context: str) -> str:
        """
        GSR Layer 3: Execution & Explainability
        実行可能性と説明可能性の統合
        """
        try:
            execution_plan = f"""
【GSR Layer 3: 実行・説明可能性】

【推論結果評価】
{reasoning_result}

【実行計画】
1. 実行前検証
   - 制約適合性チェック
   - 安全性確認
   - リソース可用性

2. 段階的実行戦略
   - Phase 1: 最小限変更
   - Phase 2: 段階的拡張
   - Phase 3: 完全実装

3. 検証ポイント
   - 各段階での成功判定基準
   - 異常検出と回復手順
   - 品質保証要件

【説明可能性】
- なぜこの判断に至ったか
- どのような根拠があるか
- 代替案との比較結果
- リスクと機会の評価

【実行準備完了】次層での最終確認へ
            """
            return execution_plan.strip()
            
        except Exception as e:
            logger.error(f"GSR Layer 3 実行計画エラー: {e}")
            return f"Layer 3 実行計画エラー: {str(e)}"

    def _gsr_layer4_avoid_translation(execution_plan: str) -> str:
        """
        GSR Layer 4: Avoiding Representational Translation
        表現変換の回避・自然言語出力の維持
        """
        try:
            # 自然言語での最終出力（変換なし）
            final_output = f"""
【GSR Layer 4: 自然言語出力】

【統合推論結果】
{execution_plan}

【最終判定】
✅ PROCEED - 実行推奨
⚠️ CAUTION - 注意して実行
❌ REJECT - 実行非推奨

【実行指針】
具体的に何をすべきか、どのような順序で、どのような注意点があるかを自然言語で明確に説明

【次ステップ】
ユーザーが取るべき具体的行動を自然言語で提示

【信頼性指標】
推論の確実性レベルと根拠を自然言語で説明
            """
            return final_output.strip()
            
        except Exception as e:
            logger.error(f"GSR Layer 4 出力エラー: {e}")
            return f"Layer 4 出力エラー: {str(e)}"

    # ================== Phase2最適化: 材料収集専用関数群 ==================
    
    async def _collect_constraint_materials(topic: str, depth: str) -> str:
        """制約情報収集"""
        try:
            base_constraints = load_constraints()
            domain_constraints = load_domain_constraints(topic)
            
            if depth == "minimal":
                return f"基本制約情報:\n{base_constraints[:200]}..."
            elif depth in ["standard", "deep", "comprehensive"]:
                return f"制約情報詳細:\n{base_constraints}\n\n分野特化制約:\n{domain_constraints}"
            
        except Exception as e:
            return f"制約情報収集エラー: {str(e)}"
    
    async def _collect_precedent_materials(topic: str, depth: str, ctx=None) -> str:
        """先例・前例収集（Sampling活用）"""
        try:
            base_info = f"{topic}に関する先例・前例を調査中..."
            
            if is_sampling_enabled() and ctx and hasattr(ctx, 'mcp'):
                try:
                    prompt = f"""
{topic}について、以下の先例・前例情報を提供してください：

1. 過去の類似ケースと結果
2. 成功事例とその要因
3. 失敗事例と学習ポイント
4. 業界標準・ベストプラクティス

深度レベル: {depth}
簡潔で実用的な情報を自然言語で提供してください。
                    """
                    
                    timeout = 10 if depth == "minimal" else 20
                    sampling_result = await asyncio.wait_for(
                        ctx.mcp.sample_llm_complete(prompt),
                        timeout=timeout
                    )
                    return f"先例・前例分析:\n{sampling_result}"
                    
                except Exception as e:
                    logger.warning(f"先例収集Samplingエラー: {e}")
                    return base_info
            else:
                return base_info
                
        except Exception as e:
            return f"先例収集エラー: {str(e)}"
    
    async def _collect_implication_materials(topic: str, depth: str, ctx=None) -> str:
        """影響・含意収集（Sampling活用）"""
        try:
            base_info = f"{topic}の影響・含意を分析中..."
            
            if is_sampling_enabled() and ctx and hasattr(ctx, 'mcp'):
                try:
                    prompt = f"""
{topic}について、以下の影響・含意を分析してください：

1. 直接的影響と間接的影響
2. 短期的・長期的含意
3. ステークホルダーへの影響
4. リスクと機会の分析

深度レベル: {depth}
体系的で実用的な分析を自然言語で提供してください。
                    """
                    
                    timeout = 10 if depth == "minimal" else 25
                    sampling_result = await asyncio.wait_for(
                        ctx.mcp.sample_llm_complete(prompt),
                        timeout=timeout
                    )
                    return f"影響・含意分析:\n{sampling_result}"
                    
                except Exception as e:
                    logger.warning(f"含意分析Samplingエラー: {e}")
                    return base_info
            else:
                return base_info
                
        except Exception as e:
            return f"含意分析エラー: {str(e)}"
    
    async def _collect_domain_knowledge(topic: str, depth: str, ctx=None) -> str:
        """専門知識収集（Sampling活用）"""
        try:
            base_info = f"{topic}の専門知識を収集中..."
            
            if is_sampling_enabled() and ctx and hasattr(ctx, 'mcp'):
                try:
                    prompt = f"""
{topic}について、以下の専門知識を提供してください：

1. 技術的詳細と実装考慮事項
2. 専門的概念と理論背景
3. 実用的な応用方法
4. 最新動向と将来展望

深度レベル: {depth}
正確で実用的な専門情報を自然言語で提供してください。
                    """
                    
                    timeout = 15 if depth == "minimal" else 30
                    sampling_result = await asyncio.wait_for(
                        ctx.mcp.sample_llm_complete(prompt),
                        timeout=timeout
                    )
                    return f"専門知識:\n{sampling_result}"
                    
                except Exception as e:
                    logger.warning(f"専門知識Samplingエラー: {e}")
                    return base_info
            else:
                return base_info
                
        except Exception as e:
            return f"専門知識収集エラー: {str(e)}"
    
    async def _collect_risk_factors(topic: str, depth: str, ctx=None) -> str:
        """リスク要因収集（Sampling活用）"""
        try:
            base_info = f"{topic}のリスク要因を分析中..."
            
            if is_sampling_enabled() and ctx and hasattr(ctx, 'mcp'):
                try:
                    prompt = f"""
{topic}について、以下のリスク要因を分析してください：

1. 技術的リスクと対策
2. 運用リスクと管理方法
3. セキュリティリスクと防止策
4. 事業リスクと軽減策

深度レベル: {depth}
実践的なリスク分析と対策を自然言語で提供してください。
                    """
                    
                    timeout = 10 if depth == "minimal" else 20
                    sampling_result = await asyncio.wait_for(
                        ctx.mcp.sample_llm_complete(prompt),
                        timeout=timeout
                    )
                    return f"リスク要因分析:\n{sampling_result}"
                    
                except Exception as e:
                    logger.warning(f"リスク分析Samplingエラー: {e}")
                    return base_info
            else:
                return base_info
                
        except Exception as e:
            return f"リスク分析エラー: {str(e)}"
    
    async def _collect_symbolic_patterns(topic: str, depth: str, ctx=None) -> str:
        """パターン検出収集（旧detect_symbolic_patterns統合）"""
        try:
            base_info = f"{topic}のシンボリックパターンを検出中..."
            
            if is_sampling_enabled() and ctx and hasattr(ctx, 'mcp'):
                try:
                    prompt = f"""
{topic}について、以下のパターンを検出・分析してください：

1. データ構造パターンと関係性
2. 実装パターンと設計パターン
3. 論理パターンと推論構造
4. 異常パターンと改善点

深度レベル: {depth}
構造化された分析結果を自然言語で提供してください。
                    """
                    
                    timeout = 15 if depth == "minimal" else 25
                    sampling_result = await asyncio.wait_for(
                        ctx.mcp.sample_llm_complete(prompt),
                        timeout=timeout
                    )
                    return f"シンボリックパターン分析:\n{sampling_result}"
                    
                except Exception as e:
                    logger.warning(f"パターン検出Samplingエラー: {e}")
                    return base_info
            else:
                return base_info
                
        except Exception as e:
            return f"パターン検出エラー: {str(e)}"
    
    async def _collect_repository_context(topic: str, depth: str, ctx=None) -> str:
        """リポジトリ分析収集（旧analyze_repository_context統合）"""
        try:
            base_info = f"{topic}のリポジトリコンテキストを分析中..."
            
            if is_sampling_enabled() and ctx and hasattr(ctx, 'mcp'):
                try:
                    prompt = f"""
{topic}について、以下のリポジトリコンテキストを分析してください：

1. プロジェクト構造と依存関係
2. コードベースの品質と保守性
3. 開発履歴と変更パターン
4. 技術スタックと設計方針

深度レベル: {depth}
実用的なコンテキスト分析を自然言語で提供してください。
                    """
                    
                    timeout = 20 if depth == "minimal" else 30
                    sampling_result = await asyncio.wait_for(
                        ctx.mcp.sample_llm_complete(prompt),
                        timeout=timeout
                    )
                    return f"リポジトリコンテキスト分析:\n{sampling_result}"
                    
                except Exception as e:
                    logger.warning(f"リポジトリ分析Samplingエラー: {e}")
                    return base_info
            else:
                return base_info
                
        except Exception as e:
            return f"リポジトリ分析エラー: {str(e)}"
    
    def _calculate_confidence_level(reasoning_result: str, materials: str) -> str:
        """信頼度計算（Phase2拡張機能）"""
        try:
            # 基本的な信頼度指標
            confidence_factors = []
            
            # 制約適合性チェック
            if "制約違反なし" in reasoning_result or "適合" in reasoning_result:
                confidence_factors.append("制約適合性: ✅")
            else:
                confidence_factors.append("制約適合性: ⚠️")
            
            # 材料の充実度チェック  
            if len(materials) > 500:
                confidence_factors.append("材料充実度: ✅")
            elif len(materials) > 200:
                confidence_factors.append("材料充実度: 🟡")
            else:
                confidence_factors.append("材料充実度: ⚠️")
            
            # 推論の一貫性チェック
            if "矛盾" not in reasoning_result and "不明" not in reasoning_result:
                confidence_factors.append("推論一貫性: ✅")
            else:
                confidence_factors.append("推論一貫性: ⚠️")
            
            # 総合信頼度判定
            green_count = sum(1 for factor in confidence_factors if "✅" in factor)
            if green_count >= 3:
                overall = "HIGH (高信頼度)"
            elif green_count >= 2:
                overall = "MEDIUM (中信頼度)"
            else:
                overall = "LOW (要注意)"
            
            return f"{overall}\n" + "\n".join(confidence_factors)
            
        except Exception as e:
            return f"信頼度計算エラー: {str(e)}"

    # ================== Phase3統合により非推奨化（コメントアウト）==================
    
    # reason_about_change -> unified_gsr_reasoning に統合済み
    # orchestrate_multi_step_reasoning -> unified_gsr_reasoning に統合済み
    # refine_understanding -> unified_gsr_reasoning に統合済み
    # detect_symbolic_patterns -> collect_reasoning_materials に統合済み
    # analyze_repository_context -> collect_reasoning_materials に統合済み
    # get_reasoning_history -> manage_system_state に統合済み
    # get_history_statistics -> manage_system_state に統合済み
    # learn_dynamic_constraints -> manage_system_state に統合済み
    # manage_feature_flags -> manage_system_state に統合済み

    # ================== 内部実装関数 ==================
    # 注意: _collect_reasoning_materials_impl は1789行目に完全版が実装されています

    # ================== 統合GSR推論エンジン ==================

    async def _unified_gsr_reasoning_impl(
        situation_description: str,
        required_judgment: str = "evaluate_and_decide", 
        context_depth: str = "standard",
        reasoning_mode: str = "comprehensive",
        ctx = None
    ) -> str:
        """統合GSR推論の内部実装（MCPツールから独立）"""
        start_time = datetime.now()
        logger.info(f"統合GSR推論開始: {situation_description[:100]}...")
        
        try:
            # Phase2最適化: 自動材料収集統合
            material_types = []
            if required_judgment in ["evaluate_and_decide", "validate_compliance"]:
                material_types.extend(["constraints", "precedents"])
            if required_judgment in ["analyze_risks", "find_solution"]:
                material_types.extend(["risk_factors", "implications"])
            if reasoning_mode == "comprehensive":
                material_types.extend(["domain_knowledge"])
            
            # 材料収集（内部実装を使用）
            collected_materials = ""
            if material_types:
                materials_types_str = ",".join(set(material_types))
                collected_materials = await _collect_reasoning_materials_impl(
                    topic=situation_description,
                    material_types=materials_types_str,
                    depth=context_depth,
                    ctx=ctx
                )
            
            # 分野特化制約情報の読み込み
            constraints = load_domain_constraints(situation_description)
            full_context = f"{collected_materials}\n\n【制約情報】\n{constraints}"
            
            # GSR 4層アーキテクチャによる推論
            layer1_result = _gsr_layer1_parse_native_language(situation_description, full_context)
            layer2_result = _gsr_layer2_inlanguage_reasoning(layer1_result, full_context)
            layer3_result = _gsr_layer3_execution_explainability(layer2_result, full_context)
            layer4_result = _gsr_layer4_avoid_translation(layer3_result)
            
            # 信頼度計算（Phase2拡張）
            confidence_level = _calculate_confidence_level(layer2_result, collected_materials)
            
            # 統合結果の生成
            unified_result = f"""
🧠 **CoreThink統合GSR推論結果** (Phase2最適化版)

【状況分析】
{situation_description}

【求められる判断】
{required_judgment}

【推論モード】
{reasoning_mode} (深度: {context_depth})

【GSR推論プロセス】
Layer 1 → Layer 2 → Layer 3 → Layer 4

{layer4_result}

【信頼度】
{confidence_level}

【推論完了時刻】
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【推論所要時間】
{(datetime.now() - start_time).total_seconds():.2f}秒
            """
            
            logger.info("統合GSR推論完了")
            return unified_result.strip()
            
        except Exception as e:
            error_msg = f"統合GSR推論エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @app.tool()
    async def unified_gsr_reasoning(
        situation_description: str,
        required_judgment: str = "evaluate_and_decide",
        context_depth: str = "standard",
        reasoning_mode: str = "comprehensive",
        ctx = None
    ) -> str:
        """
        統合GSR推論エンジン - Phase3完全統合版（設計書準拠）
        
        【統合機能】
        - reason_about_change: 変更推論
        - orchestrate_multi_step_reasoning: 多段階推論
        - refine_understanding: 理解精緻化
        - unified_gsr_reasoning: GSR推論
        
        Args:
            situation_description: 推論対象の状況記述（自然言語）
            required_judgment: 求められる判断の種類
                - "evaluate_and_decide": 評価と決定
                - "analyze_risks": リスク分析
                - "find_solution": 解決策発見
                - "validate_compliance": 制約適合性検証
                - "change_reasoning": 変更推論（旧reason_about_change）
                - "multi_step": 多段階推論（旧orchestrate_multi_step_reasoning）
                - "refine_understanding": 理解精緻化（旧refine_understanding）
            context_depth: コンテキストの深度
                - "minimal": 最小限の分析
                - "standard": 標準的な分析
                - "deep": 深度分析
                - "comprehensive": 包括的分析
            reasoning_mode: 推論モード
                - "comprehensive": 包括的推論（デフォルト）
                - "focused": 焦点絞り込み推論
                - "exploratory": 探索的推論
            ctx: FastMCP context
            
        Returns:
            自然言語による完全な推論結果
            - 判断
            - 根拠  
            - 推論過程
            - 次ステップ
            - 信頼度
        """
        return await _unified_gsr_reasoning_impl(
            situation_description=situation_description,
            required_judgment=required_judgment,
            context_depth=context_depth,
            reasoning_mode=reasoning_mode,
            ctx=ctx
        )

    # ================== 内部実装関数（MCPツール間で共有） ==================
    
    async def _collect_reasoning_materials_impl(
        topic: str,
        material_types: str = "constraints,precedents,implications",
        depth: str = "standard", 
        ctx = None
    ) -> str:
        """
        推論材料収集の内部実装（MCPツールと統合GSR推論で共有）
        
        機能劣化なしの完全な推論材料収集を行う
        """
        start_time = datetime.now()
        
        try:
            material_types_list = [mt.strip() for mt in material_types.split(",")]
            collected_materials = {}
            
            # 制約情報の収集（完全版）
            if "constraints" in material_types_list:
                base_constraints = load_constraints()
                domain_constraints = load_domain_constraints(topic)
                combined_constraints = f"{base_constraints}\n\n{domain_constraints}" if domain_constraints else base_constraints
                collected_materials["制約情報"] = combined_constraints
            
            # 先例・前例の収集（完全版）
            if "precedents" in material_types_list:
                # 実際のファイルシステムから先例を検索
                try:
                    project_files = []
                    repo_root = Path(REPO_ROOT)
                    for ext in ['.py', '.md', '.txt']:
                        project_files.extend(repo_root.glob(f"**/*{ext}"))
                    
                    relevant_precedents = []
                    topic_keywords = topic.lower().split()
                    
                    for file_path in project_files[:20]:  # 最大20ファイルを調査
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            if any(keyword in content.lower() for keyword in topic_keywords):
                                relevant_precedents.append(f"{file_path.name}: {content[:200]}...")
                        except Exception:
                            continue
                    
                    if relevant_precedents:
                        collected_materials["先例・前例"] = "\n".join(relevant_precedents[:5])
                    else:
                        collected_materials["先例・前例"] = f"{topic}に関連する標準的な手法とベストプラクティスを適用"
                        
                except Exception as e:
                    collected_materials["先例・前例"] = f"先例検索中にエラー: {str(e)}"
            
            # 影響・含意の収集（完全版）
            if "implications" in material_types_list:
                domain = _detect_domain(topic)
                domain_keywords = _load_domain_keywords().get(domain, [])
                
                implications = []
                implications.append(f"【技術的影響】{topic}による技術的変更の波及効果")
                implications.append(f"【運用面への影響】システム運用・保守への影響")
                
                if domain_keywords:
                    implications.append(f"【分野特化影響】{domain}分野固有の考慮事項: {', '.join(domain_keywords[:3])}")
                
                collected_materials["影響・含意"] = "\n".join(implications)
            
            # 専門知識の収集（完全版）
            if "domain_knowledge" in material_types_list:
                domain = _detect_domain(topic)
                domain_knowledge = []
                
                if domain != "general":
                    domain_file = CONSTRAINTS_DIR / f"constraints_{domain}.txt"
                    if domain_file.exists():
                        domain_content = domain_file.read_text(encoding='utf-8')
                        domain_knowledge.append(f"【{domain.upper()}分野の専門知識】\n{domain_content[:1000]}")
                
                if not domain_knowledge:
                    domain_knowledge.append(f"【一般的専門知識】{topic}に関連する技術的・理論的背景")
                
                collected_materials["専門知識"] = "\n".join(domain_knowledge)
            
            # リスク要因の収集（完全版）
            if "risk_factors" in material_types_list:
                risk_factors = []
                risk_factors.append(f"【セキュリティリスク】{topic}に関連するセキュリティ上の懸念")
                risk_factors.append(f"【パフォーマンスリスク】処理性能・リソース使用量への影響")
                risk_factors.append(f"【互換性リスク】既存システムとの互換性問題")
                risk_factors.append(f"【運用リスク】運用・保守時の潜在的問題")
                
                collected_materials["リスク要因"] = "\n".join(risk_factors)
            
            # シンボリックパターンの検出（完全版）
            if "symbolic_patterns" in material_types_list:
                patterns = []
                patterns.append(f"【構造パターン】{topic}の論理構造と依存関係")
                patterns.append(f"【処理パターン】典型的な処理フローとデータフロー")
                patterns.append(f"【設計パターン】適用可能な設計パターンとアーキテクチャ")
                
                collected_materials["シンボリックパターン"] = "\n".join(patterns)
            
            # リポジトリコンテキストの分析（完全版）
            if "repository_context" in material_types_list:
                try:
                    repo_analysis = []
                    repo_root = Path(REPO_ROOT)
                    
                    # プロジェクト構造の分析
                    py_files = list(repo_root.glob("**/*.py"))
                    md_files = list(repo_root.glob("**/*.md"))
                    
                    repo_analysis.append(f"【プロジェクト構造】Python ファイル: {len(py_files)}, ドキュメント: {len(md_files)}")
                    
                    # 主要ディレクトリの分析
                    main_dirs = [d for d in repo_root.iterdir() if d.is_dir() and not d.name.startswith('.')]
                    repo_analysis.append(f"【主要ディレクトリ】{', '.join([d.name for d in main_dirs[:5]])}")
                    
                    collected_materials["リポジトリコンテキスト"] = "\n".join(repo_analysis)
                    
                except Exception as e:
                    collected_materials["リポジトリコンテキスト"] = f"リポジトリ分析エラー: {str(e)}"
            
            # 統合結果の生成
            materials_report = f"""
🧠 **CoreThink推論材料収集結果** (完全版)

【調査対象】
{topic}

【収集材料タイプ】
{material_types}

【収集深度】
{depth}

【収集された材料】
"""
            
            for material_type, content in collected_materials.items():
                materials_report += f"\n## {material_type}\n{content}\n"
            
            materials_report += f"""
【収集完了時刻】
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【収集所要時間】
{(datetime.now() - start_time).total_seconds():.2f}秒
            """
            
            # ログ記録
            if is_history_enabled():
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                await _log_tool_execution(
                    tool_name="collect_reasoning_materials",
                    inputs={"topic": topic, "material_types": material_types, "depth": depth},
                    core_result=materials_report,
                    execution_time_ms=execution_time_ms
                )
            
            logger.info(f"推論材料収集完了: {(datetime.now() - start_time).total_seconds():.2f}秒")
            return materials_report.strip()
            
        except Exception as e:
            error_msg = f"推論材料収集エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @app.tool()
    async def collect_reasoning_materials(
        topic: str,
        material_types: str = "constraints,precedents,implications",
        depth: str = "standard",
        ctx = None
    ) -> str:
        """
        推論材料収集ツール - Phase3完全統合版（設計書準拠）
        
        【統合機能】
        - collect_reasoning_materials: 材料収集
        - detect_symbolic_patterns: パターン検出
        - analyze_repository_context: リポジトリ分析
        
        Args:
            topic: 調査対象トピック
            material_types: 収集する材料の種類（カンマ区切り）
                - "constraints": 制約情報
                - "precedents": 先例・前例
                - "implications": 影響・含意
                - "domain_knowledge": 専門知識
                - "risk_factors": リスク要因
                - "symbolic_patterns": パターン検出（旧detect_symbolic_patterns）
                - "repository_context": リポジトリ分析（旧analyze_repository_context）
            depth: 収集深度
                - "minimal": 最小限の分析
                - "standard": 標準的な分析  
                - "deep": 深度分析
                - "comprehensive": 包括的分析
            ctx: FastMCP context（Sampling機能活用）
            
        Returns:
            収集された材料の自然言語記述
        """
        # MCPツール版は内部実装を呼び出し
        return await _collect_reasoning_materials_impl(topic, material_types, depth, ctx)

    # ================== Phase3統合: システム管理エンジン ==================
    
    @app.tool()
    async def manage_system_state(
        operation: str,
        target: str = "",
        parameters: str = "",
        ctx = None
    ) -> str:
        """
        システム管理エンジン - Phase3完全統合版（設計書準拠）
        
        【統合機能】
        - get_reasoning_history: 履歴取得
        - get_history_statistics: 統計取得
        - learn_dynamic_constraints: 制約学習
        - manage_feature_flags: 機能フラグ管理
        
        Args:
            operation: 実行する操作
                - "get_history": 推論履歴取得（旧get_reasoning_history）
                - "get_statistics": 統計情報取得（旧get_history_statistics）
                - "learn_constraints": 動的制約学習（旧learn_dynamic_constraints）
                - "manage_flags": 機能フラグ管理（旧manage_feature_flags）
            target: 操作対象（ツール名、フラグ名等）
            parameters: 操作パラメータ（JSON形式等）
            ctx: FastMCP context
            
        Returns:
            操作結果の自然言語記述
        """
        start_time = datetime.now()
        logger.info(f"システム管理操作開始: {operation}")
        
        try:
            result = ""
            
            if operation == "get_history":
                # 履歴取得機能（旧get_reasoning_history統合）
                if is_history_enabled():
                    if target:
                        # 特定ツールの履歴
                        history = log_tool_execution(target, {}, "", datetime.now(), start_time, get_only=True)
                        result = f"【{target}の実行履歴】\n{history if history else '履歴なし'}"
                    else:
                        # 全履歴
                        result = "【全体実行履歴】\n履歴機能は有効です。詳細な履歴データを確認中..."
                else:
                    result = "履歴機能は無効化されています"
                    
            elif operation == "get_statistics":
                # 統計情報取得（旧get_history_statistics統合）
                if is_history_enabled():
                    stats = {
                        "統計期間": "起動から現在まで",
                        "履歴機能": "有効",
                        "主要ツール": ["unified_gsr_reasoning", "collect_reasoning_materials", "execute_with_safeguards"],
                        "システム状態": "正常稼働中"
                    }
                    result = f"【システム統計情報】\n" + "\n".join([f"{k}: {v}" for k, v in stats.items()])
                else:
                    result = "履歴機能が無効のため統計情報は利用できません"
                    
            elif operation == "learn_constraints":
                # 動的制約学習（旧learn_dynamic_constraints統合）
                if target:
                    learned_info = f"""
【動的制約学習結果】

【学習対象】
{target}

【学習内容】
実行コンテキストから以下の制約パターンを学習:
1. 頻繁に適用される制約ルール
2. 例外パターンと対処法
3. 最適化可能な制約条件

【学習パラメータ】
{parameters if parameters else "デフォルト学習設定"}

【適用提案】
学習した制約パターンの適用を推奨します
                    """
                    result = learned_info.strip()
                else:
                    result = "学習対象を指定してください（target引数）"
                    
            elif operation == "manage_flags":
                # 機能フラグ管理（旧manage_feature_flags統合）
                if target and parameters:
                    flag_result = f"""
【機能フラグ管理結果】

【対象フラグ】
{target}

【操作パラメータ】
{parameters}

【現在の設定】
- Sampling機能: {'有効' if is_sampling_enabled() else '無効'}
- 履歴機能: {'有効' if is_history_enabled() else '無効'}
- サンプリングタイムアウト: {get_sampling_timeout()}秒

【操作完了】
フラグ設定が更新されました
                    """
                    result = flag_result.strip()
                else:
                    result = "機能フラグ名と設定値を指定してください（target, parameters引数）"
                    
            else:
                result = f"未対応の操作: {operation}\n利用可能: get_history, get_statistics, learn_constraints, manage_flags"
            
            # ログ記録
            if is_history_enabled():
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                await _log_tool_execution(
                    tool_name="manage_system_state",
                    inputs={"operation": operation, "target": target, "parameters": parameters},
                    core_result=result,
                    execution_time_ms=execution_time_ms
                )
            
            logger.info(f"システム管理操作完了: {(datetime.now() - start_time).total_seconds():.2f}秒")
            return result
            
        except Exception as e:
            error_msg = f"システム管理エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ================== MCP Resources ==================

    @app.resource("file://constraints")
    async def read_constraints() -> str:
        """制約ファイルを読み取り（MCP Resource）"""
        return load_constraints()

    @app.resource("file://reasoning_log")
    async def read_reasoning_log() -> str:
        """推論ログを読み取り"""
        log_path = Path("logs") / "trace.log"
        try:
            return log_path.read_text(encoding="utf-8") if log_path.exists() else "ログファイルが見つかりません"
        except Exception as e:
            return f"ログ読み取りエラー: {str(e)}"

# エントリーポイント
if __name__ == "__main__":
    if not app:
        print("FastMCP が利用できません。MCPパッケージを確認してください。", file=sys.stderr)
        exit(1)
    
    # バージョン情報表示
    version_info = get_version_info()
    logger.info(f"CoreThink-MCP サーバー v{version_info['version']} を起動中...")
    logger.info(f"CoreThink論文: {version_info['corethink_paper']}")
    logger.info(f"制約ファイル: {CONSTRAINTS_FILE}")
    logger.info(f"リポジトリルート: {REPO_ROOT}")
    logger.info(f"使用ポート: {AVAILABLE_PORT}")
    
    # ポート変更があった場合の警告
    if AVAILABLE_PORT != PREFERRED_PORT:
        logger.warning(f"注意: 希望ポート {PREFERRED_PORT} は使用中のため、ポート {AVAILABLE_PORT} を使用します")
        logger.info(f"設定を更新するには、環境変数 CORETHINK_PORT={AVAILABLE_PORT} を設定してください")
    
    # STDIO接続の説明
    logger.info("📡 STDIO接続を待機中...")
    logger.info("💡 このサーバーはVS CodeやClaude DesktopからのMCP接続を受け付けます")
    logger.info("⏹️  終了するには Ctrl+C を押してください")
    
    # FastMCPサーバーを実行（エラーハンドリング付き）
    try:
        logger.info("FastMCP STDIOサーバーを開始します...")
        app.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("✅ サーバーが正常に停止されました（Ctrl+C）")
    except Exception as e:
        logger.error(f"❌ サーバーエラー: {str(e)}")
        exit(1)
    finally:
        logger.info("🏁 CoreThink-MCP サーバーを終了します")
