// MCP Server Shortcut implementation

/**
 * Creates a shortcut for the specified server
 * @param {string} serverName - The name of the server
 * @param {Object} options - Configuration options
 * @returns {Object} - The created shortcut
 */
function createShortcut(serverName, options = {}) {
  console.log(`Creating shortcut for server: ${serverName}`);
  
  // Implementation goes here
  
  return {
    name: serverName,
    options: options,
    createdAt: new Date()
  };
}

module.exports = {
  createShortcut
};