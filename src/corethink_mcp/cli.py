#!/usr/bin/env python3
"""
CoreThink-MCP CLI Interface for Node.js Integration

This script provides a command-line interface for Node.js to interact
with CoreThink-MCP Python tools via subprocess calls.
"""

import sys
import json
import argparse
import asyncio
from typing import Any, Dict

# Import CoreThink-MCP tools
from corethink_mcp.server.corethink_server import create_corethink_server


async def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call a CoreThink-MCP tool and return the result."""
    try:
        # Create server instance to access tools
        server = create_corethink_server()
        
        # Find the tool handler
        tool_handlers = {
            'reason_about_change': server.reason_about_change,
            'validate_against_constraints': server.validate_against_constraints,
            'execute_with_safeguards': server.execute_with_safeguards,
            'orchestrate_multi_step_reasoning': server.orchestrate_multi_step_reasoning,
            'learn_dynamic_constraints': server.learn_dynamic_constraints,
            'analyze_context_patterns': server.analyze_context_patterns,
            'trace_execution_flow': server.trace_execution_flow,
            'synthesize_knowledge_base': server.synthesize_knowledge_base,
            'evaluate_reasoning_quality': server.evaluate_reasoning_quality,
        }
        
        if tool_name not in tool_handlers:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }
        
        # Call the tool
        handler = tool_handlers[tool_name]
        result = await handler(arguments)
        
        return {
            'success': True,
            'result': result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='CoreThink-MCP CLI for Node.js integration'
    )
    parser.add_argument(
        '--tool',
        required=True,
        help='Tool name to execute'
    )
    parser.add_argument(
        '--args',
        required=True,
        help='Tool arguments as JSON string'
    )
    
    args = parser.parse_args()
    
    try:
        # Parse arguments
        tool_arguments = json.loads(args.args)
        
        # Execute tool
        result = asyncio.run(call_tool(args.tool, tool_arguments))
        
        # Output result as JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except json.JSONDecodeError as e:
        error_result = {
            'success': False,
            'error': f'Invalid JSON arguments: {e}'
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': f'Unexpected error: {e}'
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
