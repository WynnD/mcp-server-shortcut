// MCP Server Shortcut
// Main entry point for the application

console.log('MCP Server Shortcut - Starting up...');

const { createShortcut } = require('./src/shortcut');

// Example usage
const shortcut = createShortcut('example-server', {
  port: 8080,
  secure: true
});

console.log('Created shortcut:', shortcut);
console.log('MCP Server Shortcut - Ready!');