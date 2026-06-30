import { app, BrowserWindow, ipcMain, globalShortcut } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import WebSocket from 'ws';

let mainWindow: BrowserWindow | null = null;
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

let wsClient: WebSocket | null = null;
let reconnectTimeout: NodeJS.Timeout | null = null;
let activityCheckInterval: NodeJS.Timeout | null = null;
let lastActive = Date.now();

function connectToPythonServer() {
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  if (activityCheckInterval) {
    clearInterval(activityCheckInterval);
    activityCheckInterval = null;
  }

  const tokenPath = path.join(__dirname, '../../.ipc_token');
  let token = '';

  try {
    if (fs.existsSync(tokenPath)) {
      token = fs.readFileSync(tokenPath, 'utf8').trim();
    }
  } catch (e) {
    console.warn('Failed to read IPC token file:', e);
  }

  if (!token) {
    console.log('IPC token not found yet. Retrying in 2s...');
    reconnectTimeout = setTimeout(connectToPythonServer, 2000);
    return;
  }

  console.log(`Connecting to JARVIS IPC WebSocket on port 8765...`);
  wsClient = new WebSocket(`ws://127.0.0.1:8765?token=${token}`);
  lastActive = Date.now();

  wsClient.on('open', () => {
    console.log('Successfully connected to JARVIS Python IPC Server.');
    // Periodically monitor connection health
    activityCheckInterval = setInterval(() => {
      if (wsClient && (Date.now() - lastActive > 15000)) {
        console.warn('IPC connection idle timeout (no messages from Python). Reconnecting...');
        wsClient.close();
      }
    }, 5000);
  });

  wsClient.on('message', (rawData) => {
    lastActive = Date.now();
    try {
      const message = JSON.parse(rawData.toString());
      const event = message.event;
      const payload = message.payload || {};
      console.log(`Received IPC event: ${event}`, payload);

      // Handle Heartbeat Ping
      if (event === 'Heartbeat') {
        if (wsClient && wsClient.readyState === WebSocket.OPEN) {
          wsClient.send(JSON.stringify({ action: 'HeartbeatAck', payload: {} }));
        }
        return;
      }

      if (mainWindow) {
        mainWindow.webContents.send('ipc-event', { event, payload });
        if (event === 'WakeDetected' || event === 'ListeningStarted') {
          mainWindow.show();
          mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
        } else if (event === 'ThinkingStarted') {
          mainWindow.webContents.send('wake-trigger', { state: 'Thinking' });
        } else if (event === 'TokenChunk') {
          mainWindow.webContents.send('wake-trigger', { state: 'Thinking', chunk: payload.chunk });
        } else if (event === 'ResponseComplete') {
          mainWindow.webContents.send('wake-trigger', { state: 'Speaking', response: payload.response });
        } else if (event === 'ThinkingStopped') {
          // Await speech chunk or manual transition
        } else if (event === 'SpeakingStarted') {
          mainWindow.webContents.send('wake-trigger', { state: 'Speaking' });
        } else if (event === 'SpeakingStopped' || event === 'SystemReady') {
          mainWindow.webContents.send('wake-trigger', { state: 'Sleeping' });
        } else if (event === 'AutomationStarted') {
          mainWindow.webContents.send('wake-trigger', { state: 'Processing' });
        } else if (['ProviderOnline', 'ProviderOffline', 'ProviderDegraded', 'ProviderRecovered'].includes(event)) {
          mainWindow.webContents.send('core-status-update', { event, payload });
        }
      }
    } catch (err) {
      console.error('Error parsing IPC event frame:', err);
    }
  });

  wsClient.on('close', () => {
    console.log('IPC connection closed. Reconnecting in 3s...');
    wsClient = null;
    if (activityCheckInterval) {
      clearInterval(activityCheckInterval);
      activityCheckInterval = null;
    }
    if (!reconnectTimeout) {
      reconnectTimeout = setTimeout(connectToPythonServer, 3000);
    }
  });

  wsClient.on('error', (err) => {
    console.error('IPC socket client error. Reconnecting in 3s...');
    wsClient = null;
    if (activityCheckInterval) {
      clearInterval(activityCheckInterval);
      activityCheckInterval = null;
    }
    if (!reconnectTimeout) {
      reconnectTimeout = setTimeout(connectToPythonServer, 3000);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    transparent: true,
    frame: false,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    center: true,
    show: false, // Don't show initially
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Remove menu bar
  mainWindow.setMenu(null);

  const startURL = isDev 
    ? 'http://localhost:5173' 
    : `file://${path.join(__dirname, '../dist/index.html')}`;

  mainWindow.loadURL(startURL);

  mainWindow.once('ready-to-show', () => {
    // Keep hidden initially or show for debugging
    if (isDev) {
      mainWindow?.show();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  if (isDev) {
    // Optional: open developer tools
    // mainWindow.webContents.openDevTools({ mode: 'detach' });
  }
}

app.whenReady().then(() => {
  createWindow();
  connectToPythonServer();

  // Register Global Activation Shortcuts
  // CTRL+SPACE or Win+J to summon JARVIS
  const toggleShortcut = 'CmdOrCtrl+Space';
  const registered = globalShortcut.register(toggleShortcut, () => {
    console.log(`Global Activation shortcut [${toggleShortcut}] pressed.`);
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.webContents.send('wake-trigger', { state: 'Sleeping' });
        // Let React fade out first before hiding window
        setTimeout(() => {
          mainWindow?.hide();
        }, 300);
      } else {
        mainWindow.show();
        mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
      }
    }
  });

  if (!registered) {
    console.warn('Failed to register global hotkey shortcut CmdOrCtrl+Space.');
  }

  // Also register Windows+J shortcut for secondary futuristic option
  globalShortcut.register('Super+J', () => {
    console.log('Super+J hotkey pressed. Awakening JARVIS AI HUD.');
    if (mainWindow) {
      mainWindow.show();
      mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('will-quit', () => {
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }
  if (wsClient) {
    wsClient.close();
  }
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Communication Interfaces
ipcMain.on('app-state-change', (event, state) => {
  console.log(`UI State Transition: ${state}`);
  
  // Forward state transition to Python backend
  if (wsClient && wsClient.readyState === WebSocket.OPEN) {
    wsClient.send(JSON.stringify({ action: 'ToggleWakeState', payload: { state: state } }));
  }

  if (state === 'Sleeping') {
    // Automatically hide after fadeout delay (e.g. 500ms)
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.hide();
      }
    }, 500);
  }
});

ipcMain.on('hide-window', () => {
  if (mainWindow && mainWindow.isVisible()) {
    mainWindow.hide();
  }
});

ipcMain.on('toggle-window', () => {
  if (mainWindow) {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
      mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
    }
  }
});

ipcMain.on('trigger-command', (event, command) => {
  console.log(`Forwarding triggered command presets to Python: ${command}`);
  if (wsClient && wsClient.readyState === WebSocket.OPEN) {
    wsClient.send(JSON.stringify({ action: 'TriggerCommand', payload: { command: command } }));
  } else {
    console.warn('Cannot forward command: IPC WebSocket connection not open.');
  }
});
