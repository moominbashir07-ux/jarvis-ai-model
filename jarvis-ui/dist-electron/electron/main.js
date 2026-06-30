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
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
let mainWindow = null;
const isDev = process.env.NODE_ENV === 'development' || !electron_1.app.isPackaged;
function createWindow() {
    mainWindow = new electron_1.BrowserWindow({
        width: 600,
        height: 600,
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
