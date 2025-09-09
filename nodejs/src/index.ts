import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

export interface CoreThinkResponse {
  success: boolean;
  result?: any;
  error?: string;
}

/**
 * CoreThink-MCP Node.js Server
 * 
 * This is a hybrid implementation that provides Node.js/npm ecosystem
 * compatibility while leveraging the proven Python CoreThink-MCP engine
 * for actual General Symbolics Reasoning operations.
 */
export class CoreThinkMCPServer {
  private server: Server;
  private pythonProcess?: ChildProcess;
  private pythonServerPath: string;

  constructor() {
    this.server = new Server(
      {
        name: 'corethink-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    // Find Python CoreThink-MCP server
    this.pythonServerPath = this.findPythonServer();
    this.setupHandlers();
  }

  private findPythonServer(): string {
    // Look for Python server in common locations
    const possiblePaths = [
      // Relative to this package
      path.join(__dirname, '../../src/corethink_mcp/server/corethink_server.py'),
      // System-wide Python installation
      'corethink-mcp',  // if installed via pip
      // Development setup
      path.join(__dirname, '../../../src/corethink_mcp/server/corethink_server.py'),
    ];

    for (const serverPath of possiblePaths) {
      if (fs.existsSync(serverPath)) {
        return serverPath;
      }
    }

    throw new Error('CoreThink-MCP Python server not found. Please install corethink-mcp Python package.');
  }

  private setupHandlers(): void {
    // List tools
    this.server.setRequestHandler(
      ListToolsRequestSchema,
      async () => {
        return {
          tools: [
            {
              name: 'reason_about_change',
              description: 'Apply General Symbolics Reasoning to evaluate proposed changes',
              inputSchema: {
                type: 'object',
                properties: {
                  change_description: {
                    type: 'string',
                    description: 'Natural language description of the proposed change',
                  },
                  context_info: {
                    type: 'string',
                    description: 'Additional context information (optional)',
                  },
                },
                required: ['change_description'],
              },
            },
            {
              name: 'validate_against_constraints',
              description: 'Validate proposed changes against safety constraints',
              inputSchema: {
                type: 'object',
                properties: {
                  change_description: {
                    type: 'string',
                    description: 'Description of the change to validate',
                  },
                  constraint_categories: {
                    type: 'array',
                    items: { type: 'string' },
                    description: 'Specific constraint categories to check (optional)',
                  },
                },
                required: ['change_description'],
              },
            },
            {
              name: 'execute_with_safeguards',
              description: 'Execute changes in a safe, isolated environment',
              inputSchema: {
                type: 'object',
                properties: {
                  change_description: {
                    type: 'string',
                    description: 'Description of the change to execute',
                  },
                  dry_run: {
                    type: 'boolean',
                    description: 'Whether to perform a dry run without actual execution',
                    default: true,
                  },
                },
                required: ['change_description'],
              },
            },
          ],
        };
      }
    );

    // Call tool
    this.server.setRequestHandler(
      CallToolRequestSchema,
      async (request) => {
        const { name, arguments: args } = request.params;
        
        try {
          const result = await this.callPythonTool(name, args);
          return {
            content: [
              {
                type: 'text',
                text: result.result || result.error || 'No result returned',
              },
            ],
            isError: !result.success,
          };
        } catch (error: any) {
          return {
            content: [
              {
                type: 'text',
                text: `Error calling tool ${name}: ${error?.message || 'Unknown error'}`,
              },
            ],
            isError: true,
          };
        }
      }
    );

    // List resources
    this.server.setRequestHandler(
      ListResourcesRequestSchema,
      async () => {
        return {
          resources: [
            {
              uri: 'constraints://corethink/constraints.txt',
              name: 'Safety Constraints',
              description: 'Current safety constraints configuration',
              mimeType: 'text/plain',
            },
            {
              uri: 'logs://corethink/reasoning',
              name: 'Reasoning Logs',
              description: 'Recent reasoning operations log',
              mimeType: 'text/plain',
            },
          ],
        };
      }
    );
  }

  private async callPythonTool(toolName: string, args: any): Promise<CoreThinkResponse> {
    return new Promise((resolve, reject) => {
      // Prepare the command to call Python server
      const command = 'python';
      const pythonArgs = [
        this.pythonServerPath,
        '--tool', toolName,
        '--args', JSON.stringify(args),
      ];

      const process = spawn(command, pythonArgs, {
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      let stderr = '';

      process.stdout?.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            resolve({ success: true, result });
          } catch (error) {
            // Fallback to text response
            resolve({ success: true, result: stdout.trim() });
          }
        } else {
          resolve({
            success: false,
            error: stderr.trim() || `Process exited with code ${code}`,
          });
        }
      });

      process.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  }

  async connect(transport: StdioServerTransport): Promise<void> {
    await this.server.connect(transport);
  }

  async startHTTP(port: number): Promise<void> {
    // HTTP server implementation for standalone mode
    // This would use SSEServerTransport for HTTP/SSE
    throw new Error('HTTP transport not yet implemented');
  }
}
