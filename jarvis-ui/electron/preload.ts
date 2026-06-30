import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  sendState: (state: string) => ipcRenderer.send('app-state-change', state),
  onWakeTrigger: (callback: (event: any, data: any) => void) => ipcRenderer.on('wake-trigger', callback),
  hideWindow: () => ipcRenderer.send('hide-window'),
  toggleWindow: () => ipcRenderer.send('toggle-window'),
  triggerCommand: (command: string) => ipcRenderer.send('trigger-command', command),
  onCoreStatusUpdate: (callback: (event: any, data: any) => void) => ipcRenderer.on('core-status-update', callback),
  onIpcEvent: (callback: (event: any, data: { event: string, payload: any }) => void) => ipcRenderer.on('ipc-event', callback),
});
