const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Get __dirname equivalent for CommonJS
const currentDir = path.dirname(__filename);

// Import the test runner - need to use dynamic import for ES modules
let runTests;

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(currentDir, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.loadFile(path.join(currentDir, 'renderer', 'index.html'));
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(async () => {
  // Dynamically import the ES module
  const indexModule = await import('../index.js');
  runTests = indexModule.main;
  
  createWindow();
});

// Handle test execution
ipcMain.handle('run-test', async (event, { url, prompt }) => {
  const emitUpdate = (type, data) => {
    mainWindow.webContents.send('test-update', { type, data });
  };
  
  try {
    // Create options object directly for the test run
    const testOptions = {
      url: url,
      prompt: prompt,
      ui: true,
      verbose: false
    };
    
    // Call runTests with custom options
    const results = await runTests(emitUpdate, testOptions);
    
    return { success: true, results };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

