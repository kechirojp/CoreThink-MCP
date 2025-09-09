#!/usr/bin/env node

import { CoreThinkMCPServer } from '../index';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

async function main() {
  const args = process.argv.slice(2);
  const port = args.find(arg => arg.startsWith('--port='))?.split('=')[1];
  
  try {
    const server = new CoreThinkMCPServer();
    
    if (port) {
      // HTTP/SSE transport for standalone mode
      console.error(`Starting CoreThink-MCP server on port ${port}`);
      await server.startHTTP(parseInt(port));
    } else {
      // STDIO transport for MCP client communication
      console.error('Starting CoreThink-MCP server with STDIO transport');
      const transport = new StdioServerTransport();
      await server.connect(transport);
    }
  } catch (error) {
    console.error('Failed to start CoreThink-MCP server:', error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error('Unhandled error:', error);
  process.exit(1);
});
