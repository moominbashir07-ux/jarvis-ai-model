"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
electron_1.contextBridge.exposeInMainWorld('electronAPI', {
    sendState: (state) => electron_1.ipcRenderer.send('app-state-change', state),
    onWakeTrigger: (callback) => electron_1.ipcRenderer.on('wake-trigger', callback),
    hideWindow: () => electron_1.ipcRenderer.send('hide-window'),
    toggleWindow: () => electron_1.ipcRenderer.send('toggle-window'),
});
