export {};

declare global {
  interface Window {
    electronAPI?: {
      sendState: (state: string) => void;
      onWakeTrigger: (callback: (event: any, data: any) => void) => void;
      hideWindow: () => void;
      toggleWindow: () => void;
      triggerCommand: (command: string) => void;
      onCoreStatusUpdate: (callback: (event: any, data: any) => void) => void;
      onIpcEvent: (callback: (event: any, data: { event: string, payload: any }) => void) => void;
    };
  }
}
