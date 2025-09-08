#!/usr/bin/env python3
"""
CoreThink-MCP Setup Helper
Automatically generates Claude Desktop configuration files
"""

import json
import os
import sys
from pathlib import Path

# プロジェクトディレクトリを取得してパッケージルートをsys.pathに追加
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.corethink_mcp import get_version_info
except ImportError:
    # Fallback version info if import fails
    def get_version_info():
        return {
            "version": "1.0.0",
            "paper": "arXiv:2509.00971v2 - General Symbolics Reasoning (GSR)",
            "description": "CoreThink General Symbolics Reasoning MCP Server",
            "corethink_paper": "arXiv:2509.00971v2"
        }

def get_project_root():
    """Get absolute path to CoreThink-MCP project root"""
    return Path(__file__).parent.absolute()

def get_claude_config_path():
    """Get Claude Desktop config file path for current OS"""
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"

def create_uv_config():
    """Create Claude Desktop config for UV environment"""
    project_root = get_project_root()
    
    config = {
        "mcpServers": {
            "corethink-mcp": {
                "command": "uv",
                "args": ["run", "python", "src/corethink_mcp/server/corethink_server.py"],
                "cwd": str(project_root)
            }
        }
    }
    
    return config

def create_python_config():
    """Create Claude Desktop config for standard Python environment"""
    project_root = get_project_root()
    
    # Detect virtual environment
    venv_path = project_root / ".venv"
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        venv_bin = venv_path / "Scripts"
    else:
        python_path = venv_path / "bin" / "python"
        venv_bin = venv_path / "bin"
    
    config = {
        "mcpServers": {
            "corethink-mcp": {
                "command": str(python_path),
                "args": ["src/corethink_mcp/server/corethink_server.py"],
                "cwd": str(project_root),
                "env": {
                    "PATH": f"{venv_bin}{os.pathsep}{os.environ.get('PATH', '')}"
                }
            }
        }
    }
    
    return config

def create_remote_config():
    """Create Claude web connector config for Remote MCP"""
    return {
        "name": "CoreThink-MCP",
        "description": "CoreThink General Symbolics Reasoning MCP Server",
        "url": "http://localhost:8080/mcp",
        "authentication": {
            "type": "none"
        },
        "version": "1.0.0"
    }

def create_dxt_package():
    """Create .DXT package file for Claude Desktop drag-and-drop installation"""
    project_root = get_project_root()
    version_info = get_version_info()
    
    # DXTは記事によるとZIPアーカイブ + manifest.json形式
    # Claude Desktopの新しいDrag & Drop仕様に準拠
    dxt_config = {
        # 基本的なDXTメタデータ
        "dxt_version": "0.0.1",
        "name": "CoreThink-MCP",
        "displayName": "CoreThink-MCP",
        "description": "A Model Context Protocol Server implementing CoreThink's General Symbolics Reasoning for Long Horizon Tasks",
        "version": version_info["version"],
        "author": "kechirojp",
        "license": "MIT",
        "homepage": "https://github.com/kechirojp/CoreThink-MCP",
        "repository": {
            "type": "git",
            "url": "https://github.com/kechirojp/CoreThink-MCP.git"
        },
        
        # カテゴリとキーワード
        "keywords": [
            "MCP", "CoreThink", "General Symbolics Reasoning", "GSR", 
            "AI", "LLM", "Code Generation", "Planning", "Tool Calling"
        ],
        "categories": ["AI", "Development", "Programming Languages"],
        "icon": "🧠",
        
        # 権限設定
        "permissions": ["read_clipboard", "network", "filesystem"],
        
        # MCPサーバー設定（Python環境）
        "server": {
            "type": "python",
            "entry_point": "src/corethink_mcp/server/corethink_server.py",
            "install_command": "uv add mcp[cli] fastmcp pyyaml gitpython python-dotenv aiohttp"
        },
        
        # ユーザー設定可能項目
        "user_config": {
            "corethink_repo_root": {
                "type": "string",
                "description": "Target repository root path",
                "default": "."
            },
            "corethink_port": {
                "type": "number",
                "description": "Server port (auto-detection enabled)",
                "default": 8080
            },
            "corethink_log_level": {
                "type": "string",
                "description": "Log level",
                "default": "INFO",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
            },
            "corethink_sandbox_dir": {
                "type": "string",
                "description": "Sandbox directory for safe execution",
                "default": ".sandbox"
            }
        },
        
        # Tool definitions for Claude Desktop UI
        "tools": [
            {
                "name": "reason_about_change",
                "description": "GSRに則った自然言語による推論。制約・矛盾・リスクを言語で評価。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_intent": {"type": "string", "description": "ユーザーの意図"},
                        "current_state": {"type": "string", "description": "現在の状態"},
                        "proposed_action": {"type": "string", "description": "提案されたアクション"}
                    },
                    "required": ["user_intent", "current_state", "proposed_action"]
                }
            },
            {
                "name": "validate_against_constraints",
                "description": "提案された変更が制約に違反していないか、自然言語で検証。",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "proposed_change": {"type": "string", "description": "提案された変更"},
                        "reasoning_context": {"type": "string", "description": "推論コンテキスト（オプション）"}
                    },
                    "required": ["proposed_change"]
                }
            },
            {
                "name": "execute_with_safeguards",
                "description": "安全に変更を適用（サンドボックス環境で）",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "action_description": {"type": "string", "description": "アクションの説明"},
                        "dry_run": {"type": "boolean", "description": "ドライランかどうか", "default": True}
                    },
                    "required": ["action_description"]
                }
            }
        ],
        
        # Resource definitions
        "resources": [
            {
                "uri": "file://constraints",
                "name": "CoreThink制約ファイル",
                "description": "CoreThink-MCPの安全制約定義",
                "mimeType": "text/plain"
            },
            {
                "uri": "file://reasoning_log",
                "name": "推論ログ",
                "description": "CoreThink推論プロセスのログ",
                "mimeType": "text/plain"
            }
        ],
        
        # Installation requirements
        "requirements": {
            "python": ">=3.11.12",
            "dependencies": [
                "mcp[cli]>=0.2.0", "fastmcp>=0.1.3", "pyyaml>=6.0",
                "gitpython>=3.1.43", "python-dotenv>=1.0.1", "aiohttp>=3.8.0"
            ]
        },
        
        # Metadata
        "capabilities": {
            "reasoning": {
                "general_symbolics": True, 
                "long_horizon_tasks": True, 
                "constraint_validation": True, 
                "sandbox_execution": True
            },
            "integration": {
                "claude_desktop": True, 
                "vscode": True, 
                "lm_studio": True, 
                "remote_mcp": True
            },
            "security": {
                "safe_execution": True, 
                "constraint_checking": True, 
                "sandbox_isolation": True, 
                "dry_run_mode": True
            }
        },
        
        "documentation": {
            "quickstart": "README.md",
            "setup_guide": "SETUP.md", 
            "requirements": "REQUIREMENTS.md",
            "implementation_plan": "IMPLEMENTATION_PLAN.md"
        },
        
        # CoreThink paper reference
        "corethink_paper": version_info.get("paper", "arXiv:2509.00971v2 - General Symbolics Reasoning (GSR)")
    }
    
    return dxt_config

def save_config(config, filename):
    """Save configuration to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✅ Configuration saved: {filename}")

def install_to_claude_desktop(config_type="uv"):
    """Install configuration to Claude Desktop"""
    claude_config_path = get_claude_config_path()
    
    # Create directory if not exists
    claude_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate config
    if config_type == "uv":
        config = create_uv_config()
    else:
        config = create_python_config()
    
    # Merge with existing config if exists
    if claude_config_path.exists():
        try:
            with open(claude_config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_config = {}
        
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}
        
        existing_config["mcpServers"]["corethink-mcp"] = config["mcpServers"]["corethink-mcp"]
        config = existing_config
    
    # Save config
    with open(claude_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Claude Desktop configuration installed: {claude_config_path}")
    print("🔄 Please restart Claude Desktop to load the new configuration.")

def main():
    """Main setup function"""
    project_root = get_project_root()
    print(f"🧠 CoreThink-MCP Setup Helper")
    print(f"📁 Project root: {project_root}")
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python setup_helper.py [uv|python|remote|dxt|examples|install-uv|install-python]")
        print()
        print("Commands:")
        print("  uv         - Generate UV environment config")
        print("  python     - Generate Python environment config")
        print("  remote     - Generate Remote MCP config")
        print("  dxt        - Generate .DXT package for Claude Desktop drag & drop")
        print("  examples   - Generate all example configs")
        print("  install-uv - Install UV config to Claude Desktop")
        print("  install-python - Install Python config to Claude Desktop")
        return
    
    command = sys.argv[1]
    
    if command == "uv":
        config = create_uv_config()
        save_config(config, project_root / "claude_desktop_config_uv.json")
        
    elif command == "python":
        config = create_python_config()
        save_config(config, project_root / "claude_desktop_config_python.json")
        
    elif command == "remote":
        config = create_remote_config()
        save_config(config, project_root / "claude_web_connector.json")
        print("📝 To use Remote MCP:")
        print("1. Start remote server: python src/corethink_mcp/server/remote_server.py")
        print("2. Add custom connector in claude.ai Settings > Connectors")
        print("3. Use URL: http://localhost:8080/mcp")
        
    elif command == "dxt":
        config = create_dxt_package()
        save_config(config, project_root / "corethink-mcp.dxt")
        print("📦 .DXT package created!")
        print("🎯 To install:")
        print("1. Open Claude Desktop")
        print("2. Go to Extensions/拡張機能")
        print("3. Drag and drop corethink-mcp.dxt into the install area")
        print("4. Follow the installation prompts")
        
    elif command == "examples":
        # Generate all example configs including DXT
        configs = [
            (create_uv_config(), "claude_desktop_config_uv.example.json"),
            (create_python_config(), "claude_desktop_config_python.example.json"),
            (create_remote_config(), "claude_web_connector.example.json"),
            (create_dxt_package(), "corethink-mcp.example.dxt")
        ]
        
        for config, filename in configs:
            save_config(config, project_root / filename)
            
    elif command == "install-uv":
        install_to_claude_desktop("uv")
        
    elif command == "install-python":
        install_to_claude_desktop("python")
        
    else:
        print(f"❌ Unknown command: {command}")
        return 1
    
    print()
    print("🎉 Setup complete!")
    return 0

if __name__ == "__main__":
    exit(main())
