#!/usr/bin/env python3
"""
CoreThink-MCP 自動同期テストスクリプト
"""

import sys
from pathlib import Path
from sync_generator import ToolExtractor, PythonToTypeScriptConverter, PROJECT_ROOT

def test_tool_extraction():
    """ツール抽出のテスト"""
    print("🧪 ツール抽出テスト開始")
    
    converter = PythonToTypeScriptConverter()
    extractor = ToolExtractor(converter)
    
    python_server_path = PROJECT_ROOT / "src" / "corethink_mcp" / "server" / "corethink_server.py"
    
    if not python_server_path.exists():
        print(f"❌ Pythonサーバーファイルが見つかりません: {python_server_path}")
        return False
    
    tools = extractor.extract_tools(python_server_path)
    
    print(f"✅ {len(tools)}個のツールを抽出:")
    for tool in tools:
        print(f"  📋 {tool.name}")
        print(f"     📝 説明: {tool.description[:50]}...")
        print(f"     🔧 引数: {len(tool.arguments)}個")
        for arg in tool.arguments:
            print(f"       - {arg.name}: {arg.type_hint} → {arg.typescript_type}")
        print()
    
    return len(tools) > 0

def test_syntax_conversion():
    """構文変換のテスト"""
    print("🧪 構文変換テスト開始")
    
    converter = PythonToTypeScriptConverter()
    
    test_cases = [
        ('f"Hello {name}"', '`Hello ${name}`'),
        ('except ValueError:', 'catch (error):'),
        ('raise Exception("error")', 'throw Exception("error")'),
        ('True', 'true'),
        ('False', 'false'),
        ('None', 'null'),
        ('name.strip()', 'name.trim()'),
        ('len(items)', 'items.length'),
    ]
    
    for python_code, expected in test_cases:
        result = converter.convert_syntax(python_code)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{python_code}' → '{result}'")
        if result != expected:
            print(f"     期待値: '{expected}'")
    
    return True

def test_type_conversion():
    """型変換のテスト"""
    print("🧪 型変換テスト開始")
    
    converter = PythonToTypeScriptConverter()
    
    test_cases = [
        ('str', 'string'),
        ('int', 'number'),
        ('bool', 'boolean'),
        ('Optional[str]', 'string | undefined'),
        ('List[str]', 'string[]'),
        ('Dict[str, Any]', 'Record<string, any>'),
    ]
    
    for python_type, expected in test_cases:
        result = converter.convert_type(python_type)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {python_type} → {result}")
        if result != expected:
            print(f"     期待値: {expected}")
    
    return True

def main():
    """テスト実行"""
    print("🎯 CoreThink-MCP 自動同期テスト開始\n")
    
    tests = [
        test_type_conversion,
        test_syntax_conversion,
        test_tool_extraction,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ テストエラー: {e}\n")
    
    print(f"📊 テスト結果: {passed}/{len(tests)} 成功")
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
