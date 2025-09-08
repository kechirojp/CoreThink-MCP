"""
CoreThink-MCP
CoreThink論文のGeneral Symbolics Reasoningを実装したMCPサーバー
"""

__version__ = "1.0.0"
__author__ = "CoreThink-MCP Project"
__description__ = "A CoreThink General Symbolics Reasoning MCP server for long horizon tasks"
__corethink_paper__ = "arXiv:2509.00971v2"
__license__ = "MIT"

# バージョン情報を取得する便利な関数
def get_version_info():
    """バージョン情報を取得"""
    return {
        "version": __version__,
        "description": __description__,
        "corethink_paper": __corethink_paper__,
        "license": __license__,
        "author": __author__
    }
