"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const ws_1 = __importDefault(require("ws"));
let mainWindow = null;
const isDev = process.env.NODE_ENV === 'development' || !electron_1.app.isPackaged;
let wsClient = null;
let reconnectTimeout = null;
let activityCheckInterval = null;
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
    }
    catch (e) {
        console.warn('Failed to read IPC token file:', e);
    }
    if (!token) {
        console.log('IPC token not found yet. Retrying in 2s...');
        reconnectTimeout = setTimeout(connectToPythonServer, 2000);
        return;
    }
    console.log(`Connecting to JARVIS IPC WebSocket on port 8765...`);
    wsClient = new ws_1.default(`ws://127.0.0.1:8765?token=${token}`);
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
                if (wsClient && wsClient.readyState === ws_1.default.OPEN) {
                    wsClient.send(JSON.stringify({ action: 'HeartbeatAck', payload: {} }));
                }
                return;
            }
            if (mainWindow) {
                mainWindow.webContents.send('ipc-event', { event, payload });
                if (event === 'WakeDetected' || event === 'ListeningStarted') {
                    mainWindow.show();
                    mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
                }
                else if (event === 'ThinkingStarted') {
                    mainWindow.webContents.send('wake-trigger', { state: 'Thinking' });
                }
                else if (event === 'TokenChunk') {
                    mainWindow.webContents.send('wake-trigger', { state: 'Thinking', chunk: payload.chunk });
                }
                else if (event === 'ResponseComplete') {
                    mainWindow.webContents.send('wake-trigger', { state: 'Speaking', response: payload.response });
                }
                else if (event === 'ThinkingStopped') {
                    // Await speech chunk or manual transition
                }
                else if (event === 'SpeakingStarted') {
                    mainWindow.webContents.send('wake-trigger', { state: 'Speaking' });
                }
                else if (event === 'SpeakingStopped' || event === 'SystemReady') {
                    mainWindow.webContents.send('wake-trigger', { state: 'Sleeping' });
                }
                else if (event === 'AutomationStarted') {
                    mainWindow.webContents.send('wake-trigger', { state: 'Processing' });
                }
                else if (['ProviderOnline', 'ProviderOffline', 'ProviderDegraded', 'ProviderRecovered'].includes(event)) {
                    mainWindow.webContents.send('core-status-update', { event, payload });
                }
            }
        }
        catch (err) {
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
    mainWindow = new electron_1.BrowserWindow({
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
electron_1.app.whenReady().then(() => {
    createWindow();
    connectToPythonServer();
    // Register Global Activation Shortcuts
    // CTRL+SPACE or Win+J to summon JARVIS
    const toggleShortcut = 'CmdOrCtrl+Space';
    const registered = electron_1.globalShortcut.register(toggleShortcut, () => {
        console.log(`Global Activation shortcut [${toggleShortcut}] pressed.`);
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.webContents.send('wake-trigger', { state: 'Sleeping' });
                // Let React fade out first before hiding window
                setTimeout(() => {
                    mainWindow?.hide();
                }, 300);
            }
            else {
                mainWindow.show();
                mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
            }
        }
    });
    if (!registered) {
        console.warn('Failed to register global hotkey shortcut CmdOrCtrl+Space.');
    }
    // Also register Windows+J shortcut for secondary futuristic option
    electron_1.globalShortcut.register('Super+J', () => {
        console.log('Super+J hotkey pressed. Awakening JARVIS AI HUD.');
        if (mainWindow) {
            mainWindow.show();
            mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
        }
    });
    electron_1.app.on('activate', () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});
electron_1.app.on('will-quit', () => {
    if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
    }
    if (wsClient) {
        wsClient.close();
    }
    electron_1.globalShortcut.unregisterAll();
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
// IPC Communication Interfaces
electron_1.ipcMain.on('app-state-change', (event, state) => {
    console.log(`UI State Transition: ${state}`);
    // Forward state transition to Python backend
    if (wsClient && wsClient.readyState === ws_1.default.OPEN) {
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
electron_1.ipcMain.on('hide-window', () => {
    if (mainWindow && mainWindow.isVisible()) {
        mainWindow.hide();
    }
});
electron_1.ipcMain.on('toggle-window', () => {
    if (mainWindow) {
        if (mainWindow.isVisible()) {
            mainWindow.hide();
        }
        else {
            mainWindow.show();
            mainWindow.webContents.send('wake-trigger', { state: 'Listening' });
        }
    }
});
electron_1.ipcMain.on('trigger-command', (event, command) => {
    console.log(`Forwarding triggered command presets to Python: ${command}`);
    if (wsClient && wsClient.readyState === ws_1.default.OPEN) {
        wsClient.send(JSON.stringify({ action: 'TriggerCommand', payload: { command: command } }));
    }
    else {
        console.warn('Cannot forward command: IPC WebSocket connection not open.');
    }
});
