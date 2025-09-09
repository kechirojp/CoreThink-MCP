#!/usr/bin/env python3
"""
CoreThink-MCP 自動同期スクリプト
PythonサーバーからNode.jsサーバーへのツール定義を自動変換
"""

import ast
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from jinja2 import Template, Environment, FileSystemLoader

# プロジェクトルートの設定
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_SERVER_PATH = PROJECT_ROOT / "src" / "corethink_mcp" / "server" / "corethink_server.py"
NODEJS_SERVER_PATH = PROJECT_ROOT / "nodejs" / "src" / "index.ts"
TEMPLATES_DIR = Path(__file__).parent / "templates"

@dataclass
class ToolArgument:
    """ツール引数の情報"""
    name: str
    type_hint: str
    typescript_type: str
    description: str = ""
    required: bool = True
    default_value: Optional[str] = None

@dataclass
class ToolDefinition:
    """ツール定義の情報"""
    name: str
    description: str
    arguments: List[ToolArgument]
    python_body: str
    typescript_body: str

class PythonToTypeScriptConverter:
    """Python → TypeScript変換エンジン"""
    
    def __init__(self):
        self.type_mappings = {
            'str': 'string',
            'int': 'number', 
            'float': 'number',
            'bool': 'boolean',
            'Any': 'any',
            'Optional[str]': 'string | undefined',
            'Optional[int]': 'number | undefined',
            'Optional[bool]': 'boolean | undefined',
            'List[str]': 'string[]',
            'List[int]': 'number[]',
            'Dict[str, Any]': 'Record<string, any>',
        }
        
        self.syntax_conversions = [
            # f-string変換
            (r'f"([^"]*)"', r'`\1`'),
            (r"f'([^']*)'", r"`\1`"),
            (r'\{([^}]+)\}', r'${\1}'),
            
            # try/except → try/catch
            (r'except (\w+)', r'catch (\1)'),
            (r'except:', r'catch (error)'),
            
            # raise → throw
            (r'raise (\w+)', r'throw \1'),
            
            # None → null/undefined
            (r'\bNone\b', 'null'),
            
            # True/False → true/false
            (r'\bTrue\b', 'true'),
            (r'\bFalse\b', 'false'),
            
            # len() → .length
            (r'len\(([^)]+)\)', r'\1.length'),
            
            # .strip() → .trim()
            (r'\.strip\(\)', '.trim()'),
            
            # .format() → template literal (簡易版)
            (r'\.format\(([^)]+)\)', r''),  # 手動調整が必要
        ]
    
    def convert_type(self, python_type: str) -> str:
        """Python型ヒント → TypeScript型"""
        return self.type_mappings.get(python_type, 'any')
    
    def convert_syntax(self, python_code: str) -> str:
        """Python構文 → TypeScript構文"""
        result = python_code
        
        for pattern, replacement in self.syntax_conversions:
            result = re.sub(pattern, replacement, result)
        
        return result

class ToolExtractor:
    """Pythonサーバーからツール定義を抽出"""
    
    def __init__(self, converter: PythonToTypeScriptConverter):
        self.converter = converter
    
    def extract_tools(self, python_file_path: Path) -> List[ToolDefinition]:
        """Pythonファイルからツール定義を抽出"""
        try:
            source_code = python_file_path.read_text(encoding='utf-8')
            tree = ast.parse(source_code)
            
            tools = []
            function_count = 0
            decorated_functions = 0
            
            # すべてのノードを再帰的に探索（If文内も含む）
            def visit_node(node, depth=0):
                nonlocal function_count, decorated_functions
                indent = "  " * depth
                
                # 通常の関数と非同期関数の両方を処理
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_count += 1
                    print(f"{indent}🔍 関数発見: {node.name} (行 {node.lineno}) {'[async]' if isinstance(node, ast.AsyncFunctionDef) else ''}")
                    
                    # デコレータ情報をデバッグ表示
                    for i, decorator in enumerate(node.decorator_list):
                        print(f"{indent}  デコレータ {i}: {ast.dump(decorator)}")
                    
                    if self._has_tool_decorator(node):
                        decorated_functions += 1
                        print(f"{indent}  ✅ ツールデコレータ発見: {node.name}")
                        tool = self._extract_tool_definition(node, source_code)
                        if tool:
                            tools.append(tool)
                        else:
                            print(f"{indent}  ❌ ツール定義抽出失敗: {node.name}")
                    else:
                        print(f"{indent}  ❌ ツールデコレータなし: {node.name}")
                
                elif isinstance(node, ast.If):
                    print(f"{indent}🔍 If文発見 (行 {node.lineno})")
                    # If文の本体を再帰的に探索
                    for child in node.body:
                        visit_node(child, depth + 1)
                    # else文も探索
                    for child in node.orelse:
                        visit_node(child, depth + 1)
                    return  # 子ノードは手動で処理したのでreturn
                
                # その他のノードも再帰的に探索
                for child in ast.iter_child_nodes(node):
                    visit_node(child, depth + 1)
            
            visit_node(tree)
            
            print(f"📊 統計: {function_count}個の関数, {decorated_functions}個のツール候補")
            return tools
            
        except Exception as e:
            print(f"❌ ツール抽出エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _has_tool_decorator(self, node) -> bool:
        """@app.tool()デコレータの有無をチェック"""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
            
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if (hasattr(decorator.func, 'attr') and 
                    decorator.func.attr == 'tool'):
                    return True
                # @app.tool() の場合
                if (hasattr(decorator.func, 'value') and 
                    hasattr(decorator.func.value, 'id') and
                    decorator.func.value.id == 'app' and
                    decorator.func.attr == 'tool'):
                    return True
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr == 'tool':
                    return True
                # app.tool の場合
                if (hasattr(decorator, 'value') and 
                    hasattr(decorator.value, 'id') and
                    decorator.value.id == 'app' and
                    decorator.attr == 'tool'):
                    return True
        return False
    
    def _extract_tool_definition(self, node, source_code: str) -> Optional[ToolDefinition]:
        """関数ノードからツール定義を抽出"""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
            
        try:
            # 関数名
            name = node.name
            
            # ドキュメント文字列
            description = ast.get_docstring(node) or f"{name}ツール"
            
            # 引数の抽出
            arguments = self._extract_arguments(node)
            
            # 関数本体の抽出
            python_body = self._extract_function_body(node, source_code)
            
            # TypeScript変換
            typescript_body = self.converter.convert_syntax(python_body)
            
            return ToolDefinition(
                name=name,
                description=description,
                arguments=arguments,
                python_body=python_body,
                typescript_body=typescript_body
            )
            
        except Exception as e:
            print(f"❌ ツール定義抽出エラー ({node.name}): {e}")
            return None
    
    def _extract_arguments(self, node) -> List[ToolArgument]:
        """関数引数の抽出"""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return []
            
        arguments = []
        
        for arg in node.args.args:
            if arg.arg == 'self':  # selfは除外
                continue
                
            # 型ヒントの取得
            python_type = 'str'  # デフォルト
            if arg.annotation:
                python_type = ast.unparse(arg.annotation)
            
            typescript_type = self.converter.convert_type(python_type)
            
            arguments.append(ToolArgument(
                name=arg.arg,
                type_hint=python_type,
                typescript_type=typescript_type,
                description=f"{arg.arg}パラメータ",
                required=True
            ))
        
        return arguments
    
    def _extract_function_body(self, node, source_code: str) -> str:
        """関数本体のコードを抽出"""
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return ""
            
        lines = source_code.split('\n')
        start_line = node.body[0].lineno - 1
        end_line = node.end_lineno - 1 if node.end_lineno else len(lines)
        
        body_lines = lines[start_line:end_line]
        
        # インデントを調整
        if body_lines:
            min_indent = min(len(line) - len(line.lstrip()) 
                           for line in body_lines if line.strip())
            body_lines = [line[min_indent:] if line.strip() else line 
                         for line in body_lines]
        
        return '\n'.join(body_lines)

class NodeJSGenerator:
    """Node.jsサーバーコード生成"""
    
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    def generate_tools_definition(self, tools: List[ToolDefinition]) -> str:
        """ツール定義部分を生成"""
        template = self.env.get_template('tools_definition.ts.j2')
        return template.render(tools=tools)
    
    def generate_tools_execution(self, tools: List[ToolDefinition]) -> str:
        """ツール実行部分を生成"""
        template = self.env.get_template('tools_execution.ts.j2')
        return template.render(tools=tools)
    
    def update_nodejs_server(self, tools: List[ToolDefinition]):
        """Node.jsサーバーファイルを更新"""
        try:
            # 既存ファイルの読み込み
            original_content = NODEJS_SERVER_PATH.read_text(encoding='utf-8')
            
            # 新しいツール定義とロジックを生成
            tools_definition = self.generate_tools_definition(tools)
            tools_execution = self.generate_tools_execution(tools)
            
            print("🔧 Node.jsサーバーファイルを更新中...")
            
            # バックアップを作成
            backup_path = NODEJS_SERVER_PATH.with_suffix('.ts.backup')
            backup_path.write_text(original_content, encoding='utf-8')
            print(f"💾 バックアップ作成: {backup_path}")
            
            # 新しいファイル内容を生成
            updated_content = self._create_updated_nodejs_content(
                original_content, tools_definition, tools_execution, tools
            )
            
            # ファイルに書き込み
            NODEJS_SERVER_PATH.write_text(updated_content, encoding='utf-8')
            
            print(f"✅ Node.jsサーバー更新完了: {len(tools)}個のツール")
            print(f"📁 更新ファイル: {NODEJS_SERVER_PATH}")
            
        except Exception as e:
            print(f"❌ Node.jsサーバー更新エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_updated_nodejs_content(self, original: str, tools_def: str, tools_exec: str, tools: List[ToolDefinition]) -> str:
        """Node.jsサーバーの完全な新しい内容を生成"""
        # 生成された新しいファイル内容を出力ファイルに保存
        output_file = NODEJS_SERVER_PATH.parent / "index_generated.ts"
        
        # 現在のNode.jsサーバーの基本構造を保持しつつ、ツール部分のみ置換
        new_content = f"""// 🤖 CoreThink-MCP Node.js Server (自動生成)
// 生成日時: {json.dumps(str(__import__('datetime').datetime.now()), ensure_ascii=False)}
// 元ファイル: {NODEJS_SERVER_PATH}

import {{ Server }} from '@modelcontextprotocol/sdk/server/index.js';
import {{ StdioServerTransport }} from '@modelcontextprotocol/sdk/server/stdio.js';
import {{
  CallToolRequestSchema,
  ListToolsRequestSchema,
}} from '@modelcontextprotocol/sdk/types.js';

class CoreThinkServer {{
  private server: Server;

  constructor() {{
    this.server = new Server(
      {{
        name: 'corethink-mcp-nodejs',
        version: '1.0.0',
      }},
      {{
        capabilities: {{
          tools: {{}},
        }},
      }}
    );

    this.setupHandlers();
  }}

  private setupHandlers(): void {{
    // ツール一覧の提供
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {{
      return {{
        tools: [
{tools_def}
        ]
      }};
    }});

    // ツール実行の処理
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {{
      const {{ name: toolName, arguments: args }} = request.params;
      
      try {{
        const result = await this.executeToolDirectly(toolName, args || {{}});
        return {{
          content: [
            {{
              type: 'text',
              text: result,
            }},
          ],
        }};
      }} catch (error) {{
        return {{
          content: [
            {{
              type: 'text',
              text: `❌ エラー: ${{error instanceof Error ? error.message : String(error)}}`,
            }},
          ],
        }};
      }}
    }});
  }}

  private async executeToolDirectly(toolName: string, args: Record<string, unknown>): Promise<string> {{
    switch (toolName) {{
{tools_exec}
      
      default:
        throw new Error(`❌ 未知のツール: ${{toolName}}`);
    }}
  }}

  async run(): Promise<void> {{
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    
    // エラーハンドリング
    process.on('SIGINT', async () => {{
      console.error('🛑 SIGINT受信、サーバーを終了します...');
      await this.server.close();
      process.exit(0);
    }});
  }}
}}

const server = new CoreThinkServer();
server.run().catch((error) => {{
  console.error('❌ サーバー実行エラー:', error);
  process.exit(1);
}});
"""
        
        # 生成されたファイルも保存（確認用）
        output_file.write_text(new_content, encoding='utf-8')
        print(f"📄 生成ファイル保存: {output_file}")
        
        return new_content

def main():
    """メイン実行関数"""
    print("🚀 CoreThink-MCP 自動同期スクリプト開始")
    
    # 1. Pythonサーバーからツール抽出
    print("📖 Pythonサーバーからツール抽出中...")
    converter = PythonToTypeScriptConverter()
    extractor = ToolExtractor(converter)
    tools = extractor.extract_tools(PYTHON_SERVER_PATH)
    
    if not tools:
        print("❌ ツールが見つかりませんでした")
        return 1
    
    print(f"✅ {len(tools)}個のツールを抽出しました:")
    for tool in tools:
        print(f"  - {tool.name}: {len(tool.arguments)}個の引数")
    
    # 2. Node.jsサーバーコード生成
    print("\n🔧 Node.jsサーバーコード生成中...")
    generator = NodeJSGenerator()
    generator.update_nodejs_server(tools)
    
    print("\n🎉 自動同期スクリプト完了!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
