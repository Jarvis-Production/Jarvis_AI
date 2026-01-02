const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;

// Функция для запуска Python backend
function startBackend() {
  if (backendProcess) {
    return;
  }
  
  console.log('Starting Jarvis AI backend...');
  
  // Определяем команду Python в зависимости от ОС
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  const pythonPath = path.join(__dirname, '..', 'backend', 'main.py');
  
  // Проверяем существование файла main.py
  if (!fs.existsSync(pythonPath)) {
    console.error('Backend main.py not found at:', pythonPath);
    return;
  }
  
  backendProcess = spawn(pythonCmd, [pythonPath], {
    cwd: path.join(__dirname, '..'),
    env: {
      ...process.env,
      PYTHONPATH: path.join(__dirname, '..')
    },
    stdio: 'pipe'
  });
  
  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });
  
  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });
  
  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
    backendProcess = null;
  });
  
  backendProcess.on('error', (error) => {
    console.error('Failed to start backend:', error);
    backendProcess = null;
  });
}

// Функция для остановки backend
function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

// Создание главного окна
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webSecurity: false, // Разрешаем загрузку локальных ресурсов
      allowRunningInsecureContent: true
    },
    icon: path.join(__dirname, 'assets', 'icon.png'), // Путь к иконке
    show: false // Не показываем до готовности
  });
  
  // Загружаем приложение
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // Открываем DevTools в режиме разработки
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
  }
  
  // Показываем окно когда готово
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });
  
  // Обработка закрытия окна
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Создание меню приложения
function createMenu() {
  const template = [
    {
      label: 'Файл',
      submenu: [
        {
          label: 'Выход',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Вид',
      submenu: [
        { role: 'reload', label: 'Обновить' },
        { role: 'forceReload', label: 'Принудительно обновить' },
        { role: 'toggleDevTools', label: 'Инструменты разработчика' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Сбросить масштаб' },
        { role: 'zoomIn', label: 'Увеличить' },
        { role: 'zoomOut', label: 'Уменьшить' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Полноэкранный режим' }
      ]
    },
    {
      label: 'Окно',
      submenu: [
        { role: 'minimize', label: 'Свернуть' },
        { role: 'close', label: 'Закрыть' }
      ]
    },
    {
      label: 'Помощь',
      submenu: [
        {
          label: 'О программе',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'О программе',
              message: 'Jarvis AI Assistant',
              detail: 'Версия 1.0.0\n\nИИ-ассистент для вашего рабочего стола.'
            });
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC обработчики
ipcMain.handle('start-backend', async () => {
  startBackend();
  return { success: true };
});

ipcMain.handle('stop-backend', async () => {
  stopBackend();
  return { success: true };
});

ipcMain.handle('get-backend-status', async () => {
  return { running: backendProcess !== null };
});

ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

// События приложения
app.whenReady().then(() => {
  createWindow();
  createMenu();
  
  // Запускаем backend
  startBackend();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// Безопасность: предотвращаем создание новых окон
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
  });
});

console.log('Jarvis AI Desktop Application Starting...');