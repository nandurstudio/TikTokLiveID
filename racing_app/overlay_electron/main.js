const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;
let configData = {};

// Load config.json from parent directory
function loadConfig() {
  try {
    const configPath = path.join(__dirname, '..', 'config.json');
    if (fs.existsSync(configPath)) {
      const rawData = fs.readFileSync(configPath, 'utf8');
      const config = JSON.parse(rawData);
      configData = config.overlay || {};
      console.log('✅ Config loaded:', configData);
      return true;
    } else {
      console.warn('⚠️  config.json not found, using defaults');
      return false;
    }
  } catch (error) {
    console.error('❌ Error loading config:', error);
    return false;
  }
}

function createWindow() {
  // Default settings dari config.json
  const windowConfig = {
    width: configData.width || 1200,
    height: configData.height || 280,
    x: configData.x || 50,
    y: configData.y || 50,
    transparent: true,        // TRUE TRANSPARENCY ✅
    frame: false,             // Frameless window
    alwaysOnTop: configData.always_on_top !== false,  // From config or true
    resizable: configData.resizable !== false,        // From config or true
    movable: true,            // Draggable (via IPC manual drag)
    skipTaskbar: false,       // Show in taskbar
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      devTools: true          // Enable DevTools (F12)
    }
  };

  console.log('📐 Window config:', windowConfig);
  mainWindow = new BrowserWindow(windowConfig);

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
    // Save window position when drag ends
    if (mainWindow) {
      const [x, y] = mainWindow.getPosition();
      const [width, height] = mainWindow.getSize();
      saveWindowPosition(x, y, width, height);
    }
  });

  // Save position/size saat window di-resize
  mainWindow.on('resized', () => {
    if (mainWindow) {
      const [x, y] = mainWindow.getPosition();
      const [width, height] = mainWindow.getSize();
      saveWindowPosition(x, y, width, height);
    }
  });

  // Save position saat window dipindahkan (with debounce)
  mainWindow.on('move', () => {
    if (mainWindow) {
      const [x, y] = mainWindow.getPosition();
      const [width, height] = mainWindow.getSize();
      // Only save periodically, not on every move (performance)
      clearTimeout(mainWindow.positionSaveTimeout);
      mainWindow.positionSaveTimeout = setTimeout(() => {
        saveWindowPosition(x, y, width, height);
      }, 500);
    }
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

// Save window position to config.json
function saveWindowPosition(x, y, width, height) {
  try {
    const configPath = path.join(__dirname, '..', 'config.json');
    if (fs.existsSync(configPath)) {
      const rawData = fs.readFileSync(configPath, 'utf8');
      const config = JSON.parse(rawData);
      
      // Update overlay config
      if (!config.overlay) config.overlay = {};
      config.overlay.x = x;
      config.overlay.y = y;
      config.overlay.width = width;
      config.overlay.height = height;
      
      // Write back to file
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
      console.log(`✅ Position saved: x=${x}, y=${y}, w=${width}, h=${height}`);
    }
  } catch (error) {
    console.error('❌ Error saving position:', error);
  }
}

// Saat Electron ready
app.whenReady().then(() => {
  loadConfig();  // Load config before creating window
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
