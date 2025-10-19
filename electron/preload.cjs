const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  runTest: (url, prompt) => ipcRenderer.invoke('run-test', { url, prompt }),
  onTestUpdate: (callback) => ipcRenderer.on('test-update', (event, data) => callback(data)),
});

