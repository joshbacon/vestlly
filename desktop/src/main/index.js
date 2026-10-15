import { app, shell, BrowserWindow, ipcMain } from 'electron';
import fs from 'fs/promises';
import { join } from 'path';
import { electronApp, optimizer, is } from '@electron-toolkit/utils';
import icon from '../../resources/icon.png?asset';
import { reshapeByTicker } from '../renderer/src/utils/reshapeMarketData.js';

const DATA_FOLDER = join(__dirname, '../../src/data');
const WATCHLISTS_PATH = join(__dirname, '../../src/watchlists.json');
let mainWindow;

ipcMain.handle('load-watchlists', async () => {
  try {
    const raw = await fs.readFile(WATCHLISTS_PATH, 'utf-8');
    if (!raw.trim()) return [];
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
});

ipcMain.handle('save-watchlists', async (_event, watchlists) => {
  await fs.writeFile(WATCHLISTS_PATH, JSON.stringify(watchlists, null, 2), 'utf-8');
  return { success: true };
});

async function loadExports(folderPath, onProgress) {

  const files = await fs.readdir(folderPath);
  const jsonFiles = files.filter(f => f.endsWith('.json'));
  const filenameRegex = /^(.+)_(\d{4}-\d{2}-\d{2})\.json$/;

  const total = jsonFiles.length;
  let completed = 0;
  const records = [];

  const BATCH_SIZE = 10;
  for (let i = 0; i < jsonFiles.length; i += BATCH_SIZE) {
    const batch = jsonFiles.slice(i, i + BATCH_SIZE);

    const batchResults = await Promise.all(
      batch.map(async (filename) => {
        const match = filename.match(filenameRegex);
        if (!match) return null;
        console.log(match);
        const [, ticker, date] = match;

        const raw = await fs.readFile(join(folderPath, filename), 'utf-8');
        const data = JSON.parse(raw);
        return { ...data, ticker, date };
      })
    );

    records.push(...batchResults.filter(Boolean));
    completed += batch.length;
    onProgress({ completed, total });
  }

  return reshapeByTicker(records);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 700,
    show: true,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  });

  mainWindow.setMinimumSize(1000, 550);
  mainWindow.webContents.openDevTools();

  mainWindow.on('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: 'deny' };
  });

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL']);
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'));
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron');

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  });

  // IPC test
  ipcMain.on('ping', () => console.log('pong'));

  createWindow();

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });

  app.on('web-contents-created', (event, contents) => {
    contents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    contents.on('will-navigate', (event, url) => {
      if (url !== contents.getURL()) {
        event.preventDefault();
        shell.openExternal(url);
      }
    });
  });

  mainWindow.webContents.once('did-finish-load', () => {
    loadExports(DATA_FOLDER, (progress) => {
      mainWindow.webContents.send('load-progress', progress);
    }).then((data) => {
      mainWindow.webContents.send('load-complete', { success: true, data });
    }).catch((err) => {
      mainWindow.webContents.send('load-complete', { success: false, error: err.message });
    });
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});