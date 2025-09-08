"""
CoreThink-MCP ユーティリティ関数
GitPython と サンドボックス操作を担当
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import shutil

logger = logging.getLogger(__name__)

class GitSandbox:
    """Git操作とサンドボックス管理を行うクラス"""
    
    def __init__(self, repo_root: str = ".", sandbox_name: str = ".sandbox"):
        self.repo_root = Path(repo_root)
        self.sandbox_name = sandbox_name
        self.sandbox_path = self.repo_root / sandbox_name
    
    def create_sandbox(self) -> str:
        """安全な作業環境（サンドボックス）を作成"""
        try:
            # gitコマンドでworktreeを作成
            if not self.sandbox_path.exists():
                result = subprocess.run(
                    ["git", "worktree", "add", str(self.sandbox_path)],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                
                if result.returncode == 0:
                    logger.info(f"サンドボックスを作成しました: {self.sandbox_path}")
                    return str(self.sandbox_path)
                else:
                    logger.error(f"worktree作成エラー: {result.stderr}")
                    # フォールバック: 通常のディレクトリコピー
                    return self._create_copy_sandbox()
            else:
                logger.info(f"既存のサンドボックスを使用: {self.sandbox_path}")
                return str(self.sandbox_path)
                
        except Exception as e:
            logger.error(f"サンドボックス作成エラー: {e}")
            return self._create_copy_sandbox()
    
    def _create_copy_sandbox(self) -> str:
        """フォールバック: ディレクトリコピーでサンドボックス作成"""
        try:
            if self.sandbox_path.exists():
                shutil.rmtree(self.sandbox_path)
            
            # 重要なファイルのみコピー（.gitは除外）
            shutil.copytree(
                self.repo_root, 
                self.sandbox_path,
                ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.env')
            )
            
            logger.info(f"コピーサンドボックスを作成: {self.sandbox_path}")
            return str(self.sandbox_path)
            
        except Exception as e:
            logger.error(f"コピーサンドボックス作成エラー: {e}")
            return str(self.repo_root)  # 最悪の場合は元のディレクトリ
    
    def cleanup_sandbox(self) -> bool:
        """サンドボックスをクリーンアップ"""
        try:
            if self.sandbox_path.exists():
                # worktree削除を試行
                result = subprocess.run(
                    ["git", "worktree", "remove", str(self.sandbox_path)],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"worktreeサンドボックスを削除: {self.sandbox_path}")
                    return True
                else:
                    # フォールバック: 通常のディレクトリ削除
                    shutil.rmtree(self.sandbox_path)
                    logger.info(f"ディレクトリサンドボックスを削除: {self.sandbox_path}")
                    return True
            return True
            
        except Exception as e:
            logger.error(f"サンドボックス削除エラー: {e}")
            return False
    
    def get_diff(self, file_path: Optional[str] = None) -> str:
        """変更差分を取得"""
        try:
            cmd = ["git", "diff"]
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"diff取得エラー: {result.stderr}")
                return "差分取得に失敗しました"
                
        except Exception as e:
            logger.error(f"diff取得例外: {e}")
            return f"エラー: {str(e)}"
    
    def apply_patch(self, patch_content: str, dry_run: bool = True) -> Dict[str, Any]:
        """パッチを適用"""
        try:
            # パッチファイルを一時作成
            patch_file = self.sandbox_path / "temp.patch"
            patch_file.write_text(patch_content, encoding='utf-8')
            
            cmd = ["git", "apply"]
            if dry_run:
                cmd.append("--check")
            cmd.append(str(patch_file))
            
            result = subprocess.run(
                cmd,
                cwd=self.sandbox_path if not dry_run else self.repo_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            success = result.returncode == 0
            
            # 一時ファイル削除
            if patch_file.exists():
                patch_file.unlink()
            
            return {
                "success": success,
                "message": result.stdout if success else result.stderr,
                "dry_run": dry_run,
                "applied_in": str(self.sandbox_path) if not dry_run else "dry-run"
            }
            
        except Exception as e:
            logger.error(f"パッチ適用エラー: {e}")
            return {
                "success": False,
                "message": str(e),
                "dry_run": dry_run,
                "applied_in": "error"
            }

def load_constraints(constraints_file: Path) -> str:
    """制約ファイルを読み込む"""
    try:
        if constraints_file.exists():
            return constraints_file.read_text(encoding="utf-8")
        else:
            logger.warning(f"制約ファイルが見つかりません: {constraints_file}")
            return "制約ファイルが見つかりません"
    except Exception as e:
        logger.error(f"制約ファイル読み込みエラー: {e}")
        return f"読み込みエラー: {str(e)}"

def validate_change_against_constraints(
    change_description: str, 
    constraints: str
) -> Dict[str, Any]:
    """変更内容を制約に対して検証（簡易版）"""
    
    violations = []
    warnings = []
    
    # 簡易的なルールチェック
    change_lower = change_description.lower()
    
    # NEVER制約のチェック
    if "print(" in change_lower or "console.log" in change_lower:
        violations.append("NEVER: デバッグ出力の追加が検出されました")
    
    # MUST制約のチェック
    if "api" in change_lower and ("public" in change_lower or "external" in change_lower):
        violations.append("MUST: 公開API変更の可能性があります")
    
    # SHOULD制約のチェック
    if "def " in change_lower or "function" in change_lower:
        warnings.append("SHOULD: 関数変更時はdocstring更新を推奨")
    
    return {
        "violations": violations,
        "warnings": warnings,
        "has_violations": len(violations) > 0,
        "has_warnings": len(warnings) > 0,
        "judgment": "REJECT" if violations else ("CAUTION" if warnings else "PROCEED")
    }
