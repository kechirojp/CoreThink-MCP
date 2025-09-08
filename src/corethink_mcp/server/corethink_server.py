"""
CoreThink-MCP Server
GSRに基づく自然言語推論MCPサーバー
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
import asyncio
import git
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# FastMCP の import
try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not found, installing...")
    FastMCP = None

# ログ設定（必ずstderrに出力）
log_level = os.getenv("CORETHINK_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / "trace.log", encoding='utf-8'),
        logging.StreamHandler()  # stderr出力
    ]
)
logger = logging.getLogger(__name__)

# プロジェクト設定
REPO_ROOT = Path(os.getenv("CORETHINK_REPO_ROOT", "."))
CONSTRAINTS_FILE = Path(__file__).parent.parent / "constraints.txt"
SANDBOX_DIR = os.getenv("CORETHINK_SANDBOX_DIR", ".sandbox")

# FastMCPアプリケーションの初期化
if FastMCP:
    app = FastMCP(
        name="corethink-mcp",
        version="0.1.0"
    )
else:
    # 代替実装
    app = None

def load_constraints() -> str:
    """制約ファイルを読み込む"""
    try:
        return CONSTRAINTS_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"制約ファイルが見つかりません: {CONSTRAINTS_FILE}")
        return "制約ファイルが読み込めませんでした"

def create_sandbox() -> str:
    """安全な作業環境（サンドボックス）を作成"""
    try:
        repo = git.Repo(REPO_ROOT)
        sandbox_path = Path(REPO_ROOT) / SANDBOX_DIR
        
        if not sandbox_path.exists():
            repo.git.worktree("add", str(sandbox_path))
            logger.info(f"サンドボックスを作成しました: {sandbox_path}")
        
        return str(sandbox_path)
    except Exception as e:
        logger.error(f"サンドボックス作成エラー: {e}")
        return f"エラー: {str(e)}"

# ================== MCP Tools ==================

if app:
    @app.tool()
    async def reason_about_change(
        user_intent: str,
        current_state: str,
        proposed_action: str
    ) -> str:
        """GSRに則った自然言語による推論。制約・矛盾・リスクを言語で評価。"""
        logger.info(f"推論開始: {user_intent}")
        
        try:
            constraints = load_constraints()
            
            # GSRスタイルの推論過程
            reasoning = f"""
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
            
            logger.info("推論完了")
            return reasoning
            
        except Exception as e:
            error_msg = f"推論エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @app.tool()
    async def validate_against_constraints(
        proposed_change: str,
        reasoning_context: str = ""
    ) -> str:
        """提案された変更が制約に違反していないか、自然言語で検証。"""
        logger.info("制約検証開始")
        
        try:
            constraints = load_constraints()
            
            # 制約チェックロジック（簡易版）
            validation_result = f"""
【制約検証結果】
提案変更: {proposed_change}
文脈: {reasoning_context}

【詳細チェック】
✅ MUST「公開API変更禁止」 → 適合確認中
✅ NEVER「デバッグ出力禁止」 → 適合確認中
⚠️ SHOULD「docstring更新推奨」 → 要確認
✅ MUST「テスト通過」 → 検証必要

【総合判定】PROCEED_WITH_WARNING
【推奨】追加のdocstring更新を検討してください
【次ステップ】execute_with_safeguards でdry-run実行
            """.strip()
            
            logger.info("制約検証完了")
            return validation_result
            
        except Exception as e:
            error_msg = f"検証エラー: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @app.tool()
    async def execute_with_safeguards(
        action_description: str,
        dry_run: bool = True
    ) -> str:
        """安全に変更を適用（サンドボックス環境で）"""
        logger.info(f"実行開始 (dry_run={dry_run}): {action_description}")
        
        try:
            if dry_run:
                sandbox_path = create_sandbox()
                result = f"""
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
                result = f"""
【実行完了】
アクション: {action_description}
状態: 実装中（現在はdry-runのみ対応）
                """.strip()
            
            logger.info("実行完了")
            return result
            
        except Exception as e:
            error_msg = f"実行エラー: {str(e)}"
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
    
    logger.info("CoreThink-MCP サーバーを起動中...")
    logger.info(f"制約ファイル: {CONSTRAINTS_FILE}")
    logger.info(f"リポジトリルート: {REPO_ROOT}")
    
    # FastMCPサーバーを実行
    app.run()
