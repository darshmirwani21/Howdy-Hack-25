const { contextBridge, ipcRenderer } = require('electron');

// Expose IPC methods to renderer (like html_streaming does)
contextBridge.exposeInMainWorld('electron', {
  // Listen for messages from runner (forwarded by main process)
  onRunnerMessage: (callback) => {
    ipcRenderer.on('runner-message', (event, data) => callback(data));
  },
  // Listen for WebSocket status updates
  onWSStatus: (callback) => {
    ipcRenderer.on('ws-status', (event, status) => callback(status));
  }
});

