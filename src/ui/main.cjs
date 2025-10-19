const { app, BrowserWindow, screen } = require('electron');
const path = require('path');
const WebSocket = require('ws');

let mainWindow = null;
let ws = null;
const wsPort = process.env.WS_PORT || 9876;

function createWindow() {
  // Get primary display dimensions
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  // Calculate window position (right half of screen)
  const windowWidth = Math.floor(width / 2);
  const windowHeight = height;
  const xPosition = width - windowWidth;

  // Create the browser window
  mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: xPosition,
    y: 0,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    },
    title: 'Lumen Test Dashboard',
    backgroundColor: '#0a0a0a',
    show: false // Don't show until ready
  });

  // Load the index.html
  mainWindow.loadFile(path.join(__dirname, 'renderer.html'));

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    console.log(`Electron UI ready on port ${wsPort}`);
    
    // Open DevTools only in development
    if (process.env.NODE_ENV === 'development') {
      mainWindow.webContents.openDevTools();
    }
    
    // Connect to runner's WebSocket server
    connectToRunner();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (ws) {
      ws.close();
      ws = null;
    }
  });
}

// Connect to runner's WebSocket server (like html_streaming does)
function connectToRunner() {
  console.log(`Connecting to runner WebSocket at ws://localhost:${wsPort}...`);
  
  ws = new WebSocket(`ws://localhost:${wsPort}`);
  
  ws.onopen = () => {
    console.log('Connected to runner WebSocket!');
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('ws-status', { connected: true });
    }
  };
  
  ws.onmessage = (event) => {
    // Forward all messages from runner to renderer via IPC
    if (mainWindow && mainWindow.webContents) {
      const data = JSON.parse(event.data);
      mainWindow.webContents.send('runner-message', data);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error.message);
  };
  
  ws.onclose = () => {
    console.log('WebSocket closed');
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('ws-status', { connected: false });
    }
  };
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

