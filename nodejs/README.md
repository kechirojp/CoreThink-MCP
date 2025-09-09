# CoreThink-MCP Node.js Edition

![CoreThink-MCP Banner](https://img.shields.io/badge/CoreThink--MCP-Node.js%20Edition-green)
![NPM Version](https://img.shields.io/npm/v/@corethink/mcp)
![License](https://img.shields.io/badge/license-CC--BY--4.0-blue)

**Node.js/npm ecosystem integration for CoreThink-MCP with General Symbolics Reasoning**

## 🚀 Quick Start

### One-Click Installation for VS Code

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF)](vscode:mcp/install?%7B%22name%22%3A%22corethink%22%2C%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22%40corethink%2Fmcp%40latest%22%5D%7D)

### Manual Installation

```bash
# Install via npm
npm install -g @corethink/mcp

# Or use with npx (recommended)
npx @corethink/mcp@latest
```

### Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "corethink": {
      "command": "npx",
      "args": ["@corethink/mcp@latest"]
    }
  }
}
```

## 🎯 Features

- **🧩 General Symbolics Reasoning**: Revolutionary reasoning approach from CoreThink research
- **🔗 Hybrid Architecture**: Node.js frontend with proven Python reasoning engine
- **⚡ npm Ecosystem**: Standard Node.js installation and configuration
- **🛡️ Safety-First**: Constraint-driven validation and sandboxed execution
- **🎨 VS Code Integration**: One-click installation with official MCP support

## 🛠 Architecture

This Node.js edition uses a hybrid architecture:

```
┌─────────────────┐    ┌──────────────────────┐
│   MCP Client    │───▶│   Node.js Proxy     │
│  (VS Code etc.) │    │  @corethink/mcp     │
└─────────────────┘    └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   Python Engine     │
                       │  CoreThink-MCP      │
                       │ (GSR Implementation) │
                       └──────────────────────┘
```

**Benefits:**
- **Easy Installation**: Standard npm workflow
- **Proven Engine**: Leverages battle-tested Python implementation
- **Ecosystem Compatibility**: Works with all Node.js tooling
- **Future-Proof**: Migration path to pure TypeScript implementation

## 📦 Available Tools

### Core Reasoning Tools

- **`reason_about_change`**: Apply General Symbolics Reasoning to evaluate proposed changes
- **`validate_against_constraints`**: Validate changes against safety constraints
- **`execute_with_safeguards`**: Execute changes in isolated sandbox environment

### Advanced Reasoning Tools

- **`orchestrate_multi_step_reasoning`**: Multi-step reasoning orchestration
- **`learn_dynamic_constraints`**: Dynamic constraint learning
- **`analyze_context_patterns`**: Context pattern analysis
- **`trace_execution_flow`**: Execution flow tracing

### Cutting-Edge Tools

- **`synthesize_knowledge_base`**: Knowledge base synthesis
- **`evaluate_reasoning_quality`**: Reasoning quality evaluation

## 🔧 Requirements

- **Node.js**: 18.0.0 or higher
- **Python**: 3.11+ (for CoreThink reasoning engine)
- **MCP Client**: VS Code 1.102+, Claude Desktop, LM Studio, etc.

## 📱 Supported Applications

| Application | Setup Method | Status |
|-------------|--------------|--------|
| **VS Code 1.102+** | One-click install button | ✅ Ready |
| **Claude Desktop** | MCP configuration | ✅ Ready |
| **LM Studio** | deeplink installation | ✅ Ready |
| **Cursor** | MCP server config | ✅ Ready |

## 🚀 Usage Examples

### Basic Reasoning

```javascript
// Using VS Code with GitHub Copilot
// Simply enable CoreThink-MCP in agent mode and ask:

"Can you reason about this code change and check if it's safe?"
```

### Advanced Multi-Step Reasoning

```javascript
// Complex refactoring with safety validation
"I want to refactor this function. Can you:
1. Reason about the potential impacts
2. Validate against our safety constraints
3. Execute the change in a sandbox first"
```

## 🔒 Safety & Constraints

CoreThink-MCP includes built-in safety constraints for:

- **🏥 Medical Systems**: Patient safety and HIPAA compliance
- **⚖️ Legal Systems**: Evidence integrity and audit trails
- **🏦 Financial Systems**: Transaction safety and compliance
- **🏭 Industrial Systems**: Safety-critical operations

## 🌐 Development

### Building from Source

```bash
git clone https://github.com/kechirojp/CoreThink-MCP.git
cd CoreThink-MCP/nodejs
npm install
npm run build
```

### Testing

```bash
npm test
```

### Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md).

## 📊 Performance

CoreThink-MCP Node.js edition maintains the same reasoning quality as the Python implementation while providing:

- **Fast Startup**: ~2s initialization time
- **Low Memory**: <100MB typical usage
- **High Reliability**: Proven Python reasoning engine

## 🆔 Comparison with Python Edition

| Feature | Node.js Edition | Python Edition |
|---------|----------------|----------------|
| **Installation** | `npx @corethink/mcp` | `uv run corethink-mcp` |
| **VS Code Integration** | One-click button | Manual config |
| **Reasoning Engine** | Python (via proxy) | Native Python |
| **Performance** | ~2s startup | ~1s startup |
| **Ecosystem** | npm packages | Python packages |
| **Target Users** | JS/TS developers | Python developers |

## 🔗 Related Projects

- **[CoreThink-MCP Python](../README.md)**: Original Python implementation
- **[CoreThink Research](https://github.com/CoreThink/papers)**: Academic papers and research
- **[Model Context Protocol](https://modelcontextprotocol.io/)**: Official MCP documentation

## 📄 License

This project is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- CoreThink research team for the General Symbolics Reasoning framework
- Model Context Protocol team for the excellent MCP specification
- Node.js and TypeScript communities for the robust ecosystem

---

**🚀 Ready to enhance your development workflow with General Symbolics Reasoning?**

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Now-0098FF)](vscode:mcp/install?%7B%22name%22%3A%22corethink%22%2C%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22%40corethink%2Fmcp%40latest%22%5D%7D)
