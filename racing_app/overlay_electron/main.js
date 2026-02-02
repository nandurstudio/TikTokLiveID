const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 280,
    x: 50,
    y: 50,
    transparent: true,        // TRUE TRANSPARENCY ✅
    frame: false,             // Frameless window
    alwaysOnTop: true,        // Always on top
    resizable: true,          // Resizable
    movable: true,            // Draggable (via IPC manual drag)
    skipTaskbar: false,       // Show in taskbar
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      devTools: true          // Enable DevTools (F12)
    }
  });

  // Remove default menu completely
  mainWindow.setMenu(null);

  // Prevent system context menu on Windows
  if (process.platform === 'win32') {
    mainWindow.hookWindowMessage(278, () => {
      mainWindow.setEnabled(false);
      setTimeout(() => mainWindow.setEnabled(true), 100);
      return true;
    });
  }

  // Load HTML dari parent directory
  const htmlPath = path.join(__dirname, '..', 'live-instruction-electron.html');
  mainWindow.loadFile(htmlPath);

  // IPC Handlers untuk window control
  ipcMain.on('close-window', () => {
    if (mainWindow) mainWindow.close();
  });

  ipcMain.on('minimize-window', () => {
    if (mainWindow) mainWindow.minimize();
  });

  ipcMain.on('toggle-always-on-top', () => {
    if (mainWindow) {
      const isOnTop = mainWindow.isAlwaysOnTop();
      mainWindow.setAlwaysOnTop(!isOnTop);
      // Send status back to renderer
      mainWindow.webContents.send('always-on-top-changed', !isOnTop);
    }
  });

  // Manual window dragging IPC handlers
  ipcMain.on('start-drag', (event, { x, y }) => {
    // Store initial position for dragging
  });

  ipcMain.on('dragging', (event, { deltaX, deltaY }) => {
    if (mainWindow) {
      const [currentX, currentY] = mainWindow.getPosition();
      mainWindow.setPosition(currentX + deltaX, currentY + deltaY);
    }
  });

  ipcMain.on('stop-drag', () => {
    // Drag ended
  });

  // Shortcut: Ctrl+W untuk close
  globalShortcut.register('CommandOrControl+W', () => {
    if (mainWindow) {
      mainWindow.close();
    }
  });

  // Shortcut: Ctrl+M untuk minimize
  globalShortcut.register('CommandOrControl+M', () => {
    if (mainWindow) {
      mainWindow.minimize();
    }
  });

  // Shortcut: Ctrl+T untuk toggle always on top
  globalShortcut.register('CommandOrControl+T', () => {
    if (mainWindow) {
      const isOnTop = mainWindow.isAlwaysOnTop();
      mainWindow.setAlwaysOnTop(!isOnTop);
    }
  });

  // Shortcut: Ctrl+Shift+I untuk DevTools (debugging)
  globalShortcut.register('CommandOrControl+Shift+I', () => {
    if (mainWindow) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Log saat window ready
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('✅ Overlay loaded successfully!');
    console.log('   • Transparent background enabled');
    console.log('   • Press Ctrl+W to close');
    console.log('   • Press Ctrl+M to minimize');
    console.log('   • Press Ctrl+T to toggle always-on-top');
    console.log('   • Press Ctrl+Shift+I for DevTools');
    console.log('   • Drag window to move');
    console.log('   • Resize from edges/corners');
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Saat Electron ready
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Cleanup shortcuts
app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

// Quit saat semua window ditutup (kecuali macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
