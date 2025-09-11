"""
CoreThink-MCP 機能フラグシステム

Phase3 軽量拡張における機能の段階的有効化・無効化を管理するシステム
既存機能への影響を最小化し、安全な機能導入を実現
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FeatureFlags:
    """機能フラグ管理システム
    
    各拡張機能の有効/無効を制御し、設定の動的変更と
    緊急時の一括無効化機能を提供
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """初期化
        
        Args:
            config_file: 設定ファイルパス（環境変数 CORETHINK_FEATURE_CONFIG で上書き可能）
        """
        self.config_file = config_file or os.getenv('CORETHINK_FEATURE_CONFIG', 'conf/feature_flags.yaml')
        
        # デフォルト設定（安全第一：全機能無効）
        self.flags: Dict[str, Any] = {
            # Sampling拡張機能
            'ENABLE_SAMPLING_ENHANCEMENT': False,
            'SAMPLING_TIMEOUT_SECONDS': 5.0,
            'SAMPLING_FALLBACK_TO_CORE': True,
            
            # 履歴管理機能  
            'ENABLE_HISTORY_LOGGING': False,
            'HISTORY_MAX_FILE_SIZE_MB': 10,
            'HISTORY_FILE_PATH': 'logs/reasoning_history.md',
            'HISTORY_ROTATION_ENABLED': True,
            
            # 適応的深度制御
            'ENABLE_ADAPTIVE_DEPTH': False,
            'ADAPTIVE_DEPTH_THRESHOLD': 'auto',  # 'auto', 'low', 'medium', 'high'
            'DEPTH_CONTROL_MAX_TOOLS': 5,
            
            # パフォーマンス制御
            'MAX_CONCURRENT_TOOLS': 3,
            'TOOL_TIMEOUT_SECONDS': 30.0,
            
            # デバッグ・監視
            'ENABLE_PERFORMANCE_MONITORING': False,
            'ENABLE_DEBUG_LOGGING': False,
            
            # 緊急制御
            'EMERGENCY_DISABLE_ALL': False,
        }
        
        self._load_config()
    
    def is_enabled(self, feature_name: str) -> bool:
        """機能が有効かチェック
        
        Args:
            feature_name: 機能名
            
        Returns:
            bool: 機能が有効な場合True
        """
        # 緊急無効化チェック
        if self.flags.get('EMERGENCY_DISABLE_ALL', False):
            logger.warning(f"Feature {feature_name} disabled due to emergency mode")
            return False
        
        return self.flags.get(feature_name, False)
    
    def get_config(self, config_name: str, default: Any = None) -> Any:
        """設定値を取得
        
        Args:
            config_name: 設定名
            default: デフォルト値
            
        Returns:
            設定値
        """
        return self.flags.get(config_name, default)
    
    def set_flag(self, feature_name: str, value: Any) -> None:
        """機能フラグを設定
        
        Args:
            feature_name: 機能名
            value: 設定値
        """
        old_value = self.flags.get(feature_name)
        self.flags[feature_name] = value
        logger.info(f"Feature flag {feature_name} changed: {old_value} -> {value}")
    
    def emergency_disable(self) -> None:
        """緊急時の全機能無効化"""
        self.flags['EMERGENCY_DISABLE_ALL'] = True
        logger.critical("EMERGENCY: All enhancement features disabled")
    
    def emergency_restore(self) -> None:
        """緊急無効化の解除"""
        self.flags['EMERGENCY_DISABLE_ALL'] = False
        logger.warning("Emergency mode disabled - features restored to individual settings")
    
    def get_status_report(self) -> Dict[str, Any]:
        """現在の機能状態レポート"""
        return {
            'emergency_mode': self.flags.get('EMERGENCY_DISABLE_ALL', False),
            'sampling_enabled': self.is_enabled('ENABLE_SAMPLING_ENHANCEMENT'),
            'history_enabled': self.is_enabled('ENABLE_HISTORY_LOGGING'),
            'adaptive_depth_enabled': self.is_enabled('ENABLE_ADAPTIVE_DEPTH'),
            'performance_monitoring': self.is_enabled('ENABLE_PERFORMANCE_MONITORING'),
            'debug_logging': self.is_enabled('ENABLE_DEBUG_LOGGING'),
            'config_file': self.config_file,
        }
    
    def _load_config(self) -> None:
        """設定ファイルから設定を読み込み（存在する場合）"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            logger.info(f"Feature config file not found: {config_path}, using defaults")
            return
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    self.flags.update(loaded_config)
                    logger.info(f"Feature config loaded from: {config_path}")
        except ImportError:
            logger.warning("PyYAML not available, using default feature flags")
        except Exception as e:
            logger.error(f"Failed to load feature config: {e}, using defaults")
    
    def save_config(self) -> None:
        """現在の設定をファイルに保存"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import yaml
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.flags, f, default_flow_style=False, allow_unicode=True)
                logger.info(f"Feature config saved to: {config_path}")
        except ImportError:
            logger.warning("PyYAML not available, cannot save feature config")
        except Exception as e:
            logger.error(f"Failed to save feature config: {e}")

# グローバルインスタンス
feature_flags = FeatureFlags()

# 便利な関数群
def is_sampling_enabled() -> bool:
    """Sampling機能が有効かチェック"""
    return feature_flags.is_enabled('ENABLE_SAMPLING_ENHANCEMENT')

def is_history_enabled() -> bool:
    """履歴機能が有効かチェック"""
    return feature_flags.is_enabled('ENABLE_HISTORY_LOGGING')

def is_adaptive_depth_enabled() -> bool:
    """適応的深度制御が有効かチェック"""
    return feature_flags.is_enabled('ENABLE_ADAPTIVE_DEPTH')

def get_sampling_timeout() -> float:
    """Samplingタイムアウト時間を取得"""
    return feature_flags.get_config('SAMPLING_TIMEOUT_SECONDS', 5.0)

def get_history_file_path() -> str:
    """履歴ファイルパスを取得"""
    return feature_flags.get_config('HISTORY_FILE_PATH', 'logs/reasoning_history.md')

def emergency_disable_all() -> None:
    """緊急時の全機能無効化"""
    feature_flags.emergency_disable()

def get_feature_status() -> Dict[str, Any]:
    """機能状態レポートを取得"""
    return feature_flags.get_status_report()
