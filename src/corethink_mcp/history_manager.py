"""
CoreThink-MCP 軽量履歴管理システム

Phase3で実装される軽量履歴管理機能
複雑なCNSではなく、シンプルなMarkdown形式での推論履歴記録・管理
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .feature_flags import is_history_enabled, feature_flags

logger = logging.getLogger(__name__)

@dataclass
class ReasoningEntry:
    """推論履歴エントリ"""
    timestamp: datetime
    tool_name: str
    inputs: Dict[str, Any]
    core_result: str
    sampling_result: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None

class ReasoningHistoryManager:
    """軽量推論履歴管理システム
    
    特徴:
    - シンプルなMarkdown形式での記録
    - 可読性・検索性重視
    - ファイルベースの軽量実装
    - 必要に応じた手動編集も可能
    """
    
    def __init__(self, history_file: Optional[str] = None):
        """初期化
        
        Args:
            history_file: 履歴ファイルパス（設定ファイルから取得可能）
        """
        self.history_file = Path(history_file or feature_flags.get_config('HISTORY_FILE_PATH', 'logs/reasoning_history.md'))
        self.max_file_size = feature_flags.get_config('HISTORY_MAX_FILE_SIZE_MB', 10) * 1024 * 1024
        self.rotation_enabled = feature_flags.get_config('HISTORY_ROTATION_ENABLED', True)
        
        # ディレクトリ作成
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 初回起動時のヘッダー作成
        self._ensure_header()
    
    def log_reasoning(self, entry: ReasoningEntry) -> None:
        """推論結果をMarkdown形式で記録
        
        Args:
            entry: 推論履歴エントリ
        """
        if not is_history_enabled():
            return
        
        try:
            markdown_entry = self._format_entry(entry)
            self._append_to_file(markdown_entry)
            
            # ファイルサイズチェックとローテーション
            if self.rotation_enabled:
                self._rotate_if_needed()
                
            logger.debug(f"Reasoning entry logged: {entry.tool_name}")
            
        except Exception as e:
            logger.error(f"Failed to log reasoning entry: {e}")
    
    def search_history(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """履歴から検索
        
        Args:
            query: 検索クエリ（キーワード）
            limit: 結果数の上限
            
        Returns:
            マッチした履歴エントリのリスト
        """
        if not self.history_file.exists():
            return []
        
        try:
            results = []
            with open(self.history_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 簡易的なキーワード検索
            sections = content.split('\n## ')
            for section in sections[1:]:  # ヘッダーをスキップ
                if query.lower() in section.lower():
                    timestamp, entry_data = self._parse_section(section)
                    if timestamp and entry_data:
                        results.append({
                            'timestamp': timestamp,
                            'data': entry_data
                        })
                        if len(results) >= limit:
                            break
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search history: {e}")
            return []
    
    def get_recent_entries(self, count: int = 10) -> List[Dict[str, Any]]:
        """最近の履歴エントリを取得
        
        Args:
            count: 取得数
            
        Returns:
            最近の履歴エントリのリスト
        """
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sections = content.split('\n## ')
            recent_sections = sections[-count:] if len(sections) > count else sections[1:]
            
            results = []
            for section in reversed(recent_sections):
                timestamp, entry_data = self._parse_section(section)
                if timestamp and entry_data:
                    results.append({
                        'timestamp': timestamp,
                        'data': entry_data
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent entries: {e}")
            return []
    
    def clear_history(self) -> bool:
        """履歴をクリア
        
        Returns:
            成功した場合True
        """
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            self._ensure_header()
            logger.info("Reasoning history cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """履歴統計情報を取得
        
        Returns:
            統計情報辞書
        """
        if not self.history_file.exists():
            return {'total_entries': 0, 'file_size_mb': 0}
        
        try:
            file_size = self.history_file.stat().st_size
            with open(self.history_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entry_count = content.count('\n## ') - 1  # ヘッダーを除く
            
            return {
                'total_entries': max(0, entry_count),
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'file_path': str(self.history_file),
                'rotation_enabled': self.rotation_enabled,
                'max_size_mb': self.max_file_size / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}
    
    def _format_entry(self, entry: ReasoningEntry) -> str:
        """エントリをMarkdown形式にフォーマット"""
        timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        # 基本情報
        markdown = f"\n## {timestamp_str} - {entry.tool_name}\n\n"
        
        # 入力情報
        markdown += "**入力情報**:\n"
        for key, value in entry.inputs.items():
            # 長いテキストは切り詰め
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "..."
            markdown += f"- {key}: {value}\n"
        markdown += "\n"
        
        # CoreThink推論結果
        markdown += "**CoreThink推論結果**:\n"
        markdown += f"```\n{entry.core_result}\n```\n\n"
        
        # Sampling結果（存在する場合）
        if entry.sampling_result:
            markdown += "**Sampling補助分析**:\n"
            markdown += f"```\n{entry.sampling_result}\n```\n\n"
        
        # 実行情報
        if entry.execution_time_ms:
            markdown += f"**実行時間**: {entry.execution_time_ms:.1f}ms\n\n"
        
        # エラー情報（存在する場合）
        if entry.error:
            markdown += f"**エラー**: {entry.error}\n\n"
        
        markdown += "---\n"
        
        return markdown
    
    def _append_to_file(self, content: str) -> None:
        """ファイルにコンテンツを追加"""
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _ensure_header(self) -> None:
        """履歴ファイルのヘッダーを確保"""
        if not self.history_file.exists():
            header = f"""# CoreThink-MCP 推論履歴

> 自動生成された推論過程の記録  
> 作成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

このファイルには、CoreThink-MCPによる推論過程が時系列で記録されています。

## 記録形式

各エントリは以下の形式で記録されます：
- **入力情報**: ツールへの入力パラメータ
- **CoreThink推論結果**: GSRによる推論結果  
- **Sampling補助分析**: 補助的な分析結果（有効時のみ）
- **実行時間**: 処理時間（ミリ秒）
- **エラー**: エラー情報（発生時のみ）

---
"""
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write(header)
    
    def _rotate_if_needed(self) -> None:
        """ファイルサイズが上限を超えた場合のローテーション"""
        if not self.history_file.exists():
            return
        
        file_size = self.history_file.stat().st_size
        if file_size > self.max_file_size:
            try:
                # バックアップファイル名生成
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.history_file.with_suffix(f'.{timestamp}.md')
                
                # 現在のファイルをバックアップに移動
                self.history_file.rename(backup_path)
                
                # 新しいヘッダー作成
                self._ensure_header()
                
                logger.info(f"History file rotated: {backup_path}")
                
            except Exception as e:
                logger.error(f"Failed to rotate history file: {e}")
    
    def _parse_section(self, section: str) -> tuple[Optional[datetime], Optional[str]]:
        """履歴セクションを解析"""
        try:
            lines = section.split('\n')
            if not lines:
                return None, None
            
            # タイムスタンプ抽出
            header = lines[0]
            if ' - ' in header:
                timestamp_str = header.split(' - ')[0].strip()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                return timestamp, section
            
            return None, None
            
        except Exception:
            return None, None

# グローバルインスタンス
history_manager = ReasoningHistoryManager()

# 便利な関数群
def log_tool_execution(tool_name: str, inputs: Dict[str, Any], result: str, 
                       sampling_result: Optional[str] = None, 
                       execution_time_ms: Optional[float] = None,
                       error: Optional[str] = None) -> None:
    """ツール実行を履歴に記録"""
    entry = ReasoningEntry(
        timestamp=datetime.now(),
        tool_name=tool_name,
        inputs=inputs,
        core_result=result,
        sampling_result=sampling_result,
        execution_time_ms=execution_time_ms,
        error=error
    )
    history_manager.log_reasoning(entry)

def search_reasoning_history(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """推論履歴を検索"""
    return history_manager.search_history(query, limit)

def get_recent_reasoning(count: int = 10) -> List[Dict[str, Any]]:
    """最近の推論履歴を取得"""
    return history_manager.get_recent_entries(count)

def clear_reasoning_history() -> bool:
    """推論履歴をクリア"""
    return history_manager.clear_history()

def get_history_stats() -> Dict[str, Any]:
    """履歴統計情報を取得"""
    return history_manager.get_statistics()
