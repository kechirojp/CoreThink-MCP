#!/usr/bin/env python3
"""
CoreThink-MCP Diagnostic Tool
システムの状態を診断し、よくある問題を自動修復するツール
"""

import os
import sys
import json
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CoreThinkDiagnostic:
    """CoreThink-MCP システム診断クラス"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues_found = []
        self.fixes_applied = []
        
    def run_full_diagnostic(self) -> Dict:
        """完全診断を実行"""
        print("🔍 CoreThink-MCP システム診断を開始...")
        
        results = {
            'system_info': self.get_system_info(),
            'python_env': self.check_python_environment(),
            'dependencies': self.check_dependencies(),
            'config_files': self.check_config_files(),
            'mcp_setup': self.check_mcp_setup(),
            'domain_keywords': self.check_domain_keywords(),
            'performance': self.check_performance_settings(),
            'logs': self.analyze_logs(),
            'auto_fixes': self.apply_auto_fixes()
        }
        
        self.print_diagnostic_summary(results)
        return results
    
    def get_system_info(self) -> Dict:
        """システム情報を取得"""
        print("📋 システム情報を収集中...")
        
        info = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'hostname': platform.node(),
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        }
        
        # Python パス情報
        try:
            info['python_executable'] = sys.executable
            info['python_prefix'] = sys.prefix
            info['virtual_env'] = os.getenv('VIRTUAL_ENV', 'Not in virtual environment')
        except Exception as e:
            info['python_info_error'] = str(e)
            
        return info
    
    def check_python_environment(self) -> Dict:
        """Python環境をチェック"""
        print("🐍 Python環境をチェック中...")
        
        result = {'status': 'ok', 'issues': [], 'info': {}}
        
        # Python バージョンチェック
        version_info = sys.version_info
        if version_info < (3, 8):
            result['issues'].append(f"Python {version_info.major}.{version_info.minor}は古すぎます。Python 3.8以上が必要です。")
            result['status'] = 'error'
        
        # 仮想環境チェック
        venv = os.getenv('VIRTUAL_ENV')
        if not venv:
            result['issues'].append("仮想環境が有効化されていません。'source .venv/bin/activate' を実行してください。")
            result['status'] = 'warning'
        else:
            result['info']['virtual_env'] = venv
            
        # pip チェック
        try:
            import pip
            result['info']['pip_version'] = pip.__version__
        except ImportError:
            result['issues'].append("pip が見つかりません。Python インストールに問題があります。")
            result['status'] = 'error'
            
        return result
    
    def check_dependencies(self) -> Dict:
        """依存関係をチェック"""
        print("📦 依存関係をチェック中...")
        
        result = {'status': 'ok', 'missing': [], 'installed': [], 'issues': []}
        
        required_packages = [
            'fastmcp',
            'mcp', 
            'gitpython',
            'pydantic',
            'typing-extensions'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                result['installed'].append(package)
            except ImportError:
                result['missing'].append(package)
                result['status'] = 'error'
                
        if result['missing']:
            result['issues'].append(f"不足パッケージ: {', '.join(result['missing'])}")
            
        return result
    
    def check_config_files(self) -> Dict:
        """設定ファイルをチェック"""
        print("⚙️ 設定ファイルをチェック中...")
        
        result = {'status': 'ok', 'files': {}, 'issues': []}
        
        # Claude Desktop設定
        claude_configs = self._get_claude_config_paths()
        for name, path in claude_configs.items():
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    result['files'][name] = {
                        'path': str(path),
                        'exists': True,
                        'valid_json': True,
                        'has_corethink': 'corethink-mcp' in str(config)
                    }
                except json.JSONDecodeError:
                    result['files'][name] = {
                        'path': str(path),
                        'exists': True,
                        'valid_json': False
                    }
                    result['issues'].append(f"{name} JSONフォーマットエラー")
                    result['status'] = 'warning'
            else:
                result['files'][name] = {
                    'path': str(path),
                    'exists': False
                }
                
        return result
    
    def check_mcp_setup(self) -> Dict:
        """MCP設定をチェック"""
        print("🔗 MCP設定をチェック中...")
        
        result = {'status': 'ok', 'issues': [], 'info': {}}
        
        # pyproject.toml チェック
        pyproject_path = self.project_root / 'pyproject.toml'
        if pyproject_path.exists():
            result['info']['pyproject_exists'] = True
            try:
                # インストールモードチェック
                process = subprocess.run(
                    [sys.executable, '-c', 'import corethink_mcp; print("installed")'],
                    capture_output=True, text=True, timeout=10
                )
                if process.returncode == 0:
                    result['info']['package_installed'] = True
                else:
                    result['issues'].append("corethink_mcp パッケージがインストールされていません")
                    result['status'] = 'error'
            except subprocess.TimeoutExpired:
                result['issues'].append("パッケージインポートがタイムアウトしました")
                result['status'] = 'warning'
        else:
            result['issues'].append("pyproject.toml が見つかりません")
            result['status'] = 'error'
            
        return result
    
    def check_domain_keywords(self) -> Dict:
        """ドメインキーワード設定をチェック"""
        print("🎯 ドメインキーワードをチェック中...")
        
        result = {'status': 'ok', 'domains': {}, 'issues': []}
        
        constraints_dir = self.project_root / 'src' / 'corethink_mcp' / 'constraints'
        if not constraints_dir.exists():
            result['issues'].append("constraints ディレクトリが見つかりません")
            result['status'] = 'error'
            return result
            
        # 制約ファイルをチェック
        for constraint_file in constraints_dir.glob('constraints_*.txt'):
            domain = constraint_file.stem.replace('constraints_', '')
            try:
                with open(constraint_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                has_keywords = '## KEYWORDS' in content
                keywords_count = 0
                if has_keywords:
                    # キーワード数をカウント
                    lines = content.split('\n')
                    in_keywords = False
                    for line in lines:
                        if line.strip() == '## KEYWORDS':
                            in_keywords = True
                            continue
                        if in_keywords and line.strip().startswith('##'):
                            break
                        if in_keywords and line.strip():
                            keywords_count += len([k.strip() for k in line.split(',') if k.strip()])
                            
                result['domains'][domain] = {
                    'file_exists': True,
                    'has_keywords': has_keywords,
                    'keywords_count': keywords_count
                }
                
                if not has_keywords:
                    result['issues'].append(f"{domain} ドメインにキーワードセクションがありません")
                    result['status'] = 'warning'
                elif keywords_count == 0:
                    result['issues'].append(f"{domain} ドメインのキーワードが空です")
                    result['status'] = 'warning'
                    
            except Exception as e:
                result['domains'][domain] = {'file_exists': True, 'read_error': str(e)}
                result['issues'].append(f"{domain} ドメインファイル読み込みエラー: {e}")
                result['status'] = 'warning'
                
        if len(result['domains']) == 0:
            result['issues'].append("ドメイン制約ファイルが見つかりません")
            result['status'] = 'error'
            
        return result
    
    def check_performance_settings(self) -> Dict:
        """パフォーマンス設定をチェック"""
        print("⚡ パフォーマンス設定をチェック中...")
        
        result = {'status': 'ok', 'settings': {}, 'recommendations': []}
        
        # 環境変数チェック
        perf_vars = {
            'CORETHINK_PERFORMANCE_MODE': os.getenv('CORETHINK_PERFORMANCE_MODE'),
            'CORETHINK_CACHE_SIZE': os.getenv('CORETHINK_CACHE_SIZE'),
            'CORETHINK_PORT': os.getenv('CORETHINK_PORT')
        }
        
        result['settings']['env_vars'] = perf_vars
        
        # 推奨設定
        if not perf_vars['CORETHINK_PERFORMANCE_MODE']:
            result['recommendations'].append("CORETHINK_PERFORMANCE_MODE=fast を設定すると高速化できます")
            
        if not perf_vars['CORETHINK_CACHE_SIZE']:
            result['recommendations'].append("CORETHINK_CACHE_SIZE=1000 を設定するとキャッシュが効率化されます")
            
        # ディスク容量チェック
        try:
            import shutil
            free_bytes = shutil.disk_usage(self.project_root).free
            free_gb = free_bytes / (1024**3)
            result['settings']['disk_space_gb'] = round(free_gb, 2)
            
            if free_gb < 1:
                result['recommendations'].append("ディスク容量が少なくなっています（1GB未満）")
                
        except Exception as e:
            result['settings']['disk_check_error'] = str(e)
            
        return result
    
    def analyze_logs(self) -> Dict:
        """ログを分析"""
        print("📄 ログを分析中...")
        
        result = {'status': 'ok', 'files': {}, 'recent_errors': [], 'warnings': []}
        
        logs_dir = self.project_root / 'logs'
        if not logs_dir.exists():
            result['warnings'].append("logs ディレクトリが見つかりません")
            return result
            
        # ログファイルをチェック
        for log_file in logs_dir.glob('*.log'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                result['files'][log_file.name] = {
                    'size_mb': round(log_file.stat().st_size / (1024*1024), 2),
                    'line_count': len(lines)
                }
                
                # 最新のエラーを抽出
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                for line in recent_lines:
                    if 'ERROR' in line.upper():
                        result['recent_errors'].append(line.strip())
                    elif 'WARNING' in line.upper():
                        result['warnings'].append(line.strip())
                        
            except Exception as e:
                result['files'][log_file.name] = {'read_error': str(e)}
                
        # エラーが多い場合は警告
        if len(result['recent_errors']) > 5:
            result['status'] = 'warning'
            
        return result
    
    def apply_auto_fixes(self) -> Dict:
        """自動修復を適用"""
        print("🔧 自動修復を適用中...")
        
        result = {'applied': [], 'failed': [], 'skipped': []}
        
        # 1. 不足パッケージの自動インストール
        try:
            deps_result = self.check_dependencies()
            if deps_result['missing']:
                print(f"📦 不足パッケージを自動インストール: {deps_result['missing']}")
                for package in deps_result['missing']:
                    try:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                     check=True, capture_output=True)
                        result['applied'].append(f"パッケージ {package} をインストール")
                    except subprocess.CalledProcessError as e:
                        result['failed'].append(f"パッケージ {package} のインストール失敗: {e}")
        except Exception as e:
            result['failed'].append(f"依存関係チェック失敗: {e}")
            
        # 2. ログディレクトリの作成
        logs_dir = self.project_root / 'logs'
        if not logs_dir.exists():
            try:
                logs_dir.mkdir()
                result['applied'].append("logs ディレクトリを作成")
            except Exception as e:
                result['failed'].append(f"logs ディレクトリ作成失敗: {e}")
                
        # 3. 設定ファイルの基本チェック
        try:
            setup_helper = self.project_root / 'setup_helper.py'
            if setup_helper.exists():
                # setup_helper.py --check を実行
                process = subprocess.run([sys.executable, str(setup_helper), '--check'], 
                                       capture_output=True, text=True, timeout=30)
                if process.returncode != 0:
                    result['skipped'].append("setup_helper.py --check が失敗しました")
                else:
                    result['applied'].append("設定チェックを実行")
            else:
                result['skipped'].append("setup_helper.py が見つかりません")
        except Exception as e:
            result['failed'].append(f"設定チェック失敗: {e}")
            
        return result
    
    def _get_claude_config_paths(self) -> Dict[str, Path]:
        """Claude Desktop設定ファイルのパスを取得"""
        system = platform.system().lower()
        
        if system == 'windows':
            base = Path(os.getenv('APPDATA', '')) / 'Claude'
        elif system == 'darwin':  # macOS
            base = Path.home() / 'Library' / 'Application Support' / 'Claude'
        else:  # Linux
            base = Path.home() / '.config' / 'claude'
            
        return {
            'claude_desktop_config': base / 'claude_desktop_config.json'
        }
    
    def print_diagnostic_summary(self, results: Dict):
        """診断結果のサマリーを表示"""
        print("\n" + "="*60)
        print("📊 CoreThink-MCP 診断結果サマリー")
        print("="*60)
        
        # ステータス集計
        statuses = []
        for section, data in results.items():
            if isinstance(data, dict) and 'status' in data:
                statuses.append(data['status'])
                
        error_count = statuses.count('error')
        warning_count = statuses.count('warning')
        ok_count = statuses.count('ok')
        
        print(f"✅ 正常: {ok_count} 項目")
        print(f"⚠️  警告: {warning_count} 項目") 
        print(f"❌ エラー: {error_count} 項目")
        
        # 主要な問題を表示
        if error_count > 0:
            print(f"\n🚨 修復が必要な問題:")
            for section, data in results.items():
                if isinstance(data, dict) and data.get('status') == 'error':
                    print(f"   • {section}: {', '.join(data.get('issues', []))}")
                    
        if warning_count > 0:
            print(f"\n⚠️  注意が必要な項目:")
            for section, data in results.items():
                if isinstance(data, dict) and data.get('status') == 'warning':
                    issues = data.get('issues', [])
                    if issues:
                        print(f"   • {section}: {issues[0]}")
        
        # 自動修復結果
        auto_fixes = results.get('auto_fixes', {})
        if auto_fixes.get('applied'):
            print(f"\n🔧 自動修復完了:")
            for fix in auto_fixes['applied']:
                print(f"   • {fix}")
                
        if auto_fixes.get('failed'):
            print(f"\n❌ 自動修復失敗:")
            for fail in auto_fixes['failed']:
                print(f"   • {fail}")
        
        print(f"\n💡 詳細な修復方法は docs/FAQ.md を参照してください")
        print("="*60)


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CoreThink-MCP システム診断ツール')
    parser.add_argument('--output', '-o', help='結果をJSONファイルに出力')
    parser.add_argument('--no-auto-fix', action='store_true', help='自動修復をスキップ')
    parser.add_argument('--section', choices=['system', 'python', 'deps', 'config', 'mcp', 'keywords', 'perf', 'logs'], 
                       help='特定のセクションのみチェック')
    
    args = parser.parse_args()
    
    diagnostic = CoreThinkDiagnostic()
    
    if args.section:
        # 特定セクションのみ実行
        method_map = {
            'system': diagnostic.get_system_info,
            'python': diagnostic.check_python_environment,
            'deps': diagnostic.check_dependencies,
            'config': diagnostic.check_config_files,
            'mcp': diagnostic.check_mcp_setup,
            'keywords': diagnostic.check_domain_keywords,
            'perf': diagnostic.check_performance_settings,
            'logs': diagnostic.analyze_logs
        }
        
        if args.section in method_map:
            result = method_map[args.section]()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return
        
    # 完全診断を実行
    results = diagnostic.run_full_diagnostic()
    
    # 結果をファイルに出力
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 診断結果を {args.output} に保存しました")


if __name__ == '__main__':
    main()