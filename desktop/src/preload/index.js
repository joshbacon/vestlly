import { contextBridge, ipcRenderer, shell } from 'electron';
import { electronAPI } from '@electron-toolkit/preload';

// Custom APIs for renderer
const api = {};

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI);
    contextBridge.exposeInMainWorld('api', api);
    contextBridge.exposeInMainWorld('electronAPI', {
      onLoadProgress: (callback) => {
        ipcRenderer.on('load-progress', (_event, progress) => callback(progress));
      },
      onLoadComplete: (callback) => {
        ipcRenderer.on('load-complete', (_event, result) => callback(result));
      },
      removeLoadListeners: () => {
        ipcRenderer.removeAllListeners('load-progress');
        ipcRenderer.removeAllListeners('load-complete');
      },
      loadWatchlists: () => ipcRenderer.invoke('load-watchlists'),
      saveWatchlists: (watchlists) => ipcRenderer.invoke('save-watchlists', watchlists),
      openExternal: (url) => shell.openExternal(url),
    });
  } catch (error) {
    console.error(error);
  }
} else {
  window.electron = electronAPI;
  window.api = api;
}
