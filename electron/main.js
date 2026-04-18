const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

let tray = null
let mainWindow = null
let backendProcess = null

function startBackend() {
  const backendDir = path.resolve(app.getAppPath(), '..', 'backend')
  const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python'

  backendProcess = spawn(pythonExe, ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: backendDir,
    stdio: 'ignore',
    windowsHide: true,
  })

  backendProcess.on('error', (error) => {
    dialog.showErrorBox('FocusFlow AI backend error', String(error))
  })

  backendProcess.on('exit', (code, signal) => {
    if (code !== 0) {
      dialog.showErrorBox('FocusFlow AI backend stopped unexpectedly', `Exit code: ${code} signal: ${signal}`)
    }
  })
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill()
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(app.getAppPath(), 'preload.js'),
      contextIsolation: true,
    },
  })

  const startURL = process.env.ELECTRON_START_URL || 'http://127.0.0.1:5173'
  mainWindow.loadURL(startURL)
  mainWindow.on('minimize', (event) => {
    event.preventDefault()
    mainWindow.hide()
  })
  mainWindow.on('close', () => {
    // Backend handled externally
  })
}

function createTray() {
  const iconPath = path.join(app.getAppPath(), 'resources', 'tray.png')
  const icon = nativeImage.createFromPath(iconPath)
  tray = new Tray(icon.isEmpty() ? nativeImage.createEmpty() : icon)
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show FocusFlow', click: () => mainWindow.show() },
    { label: 'Quit', click: () => app.quit() },
  ])
  tray.setToolTip('FocusFlow AI')
  tray.setContextMenu(contextMenu)
}

ipcMain.handle('invoke-backend', async (_, method, endpoint, body) => {
  try {
    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
    const payload = await response.json()
    return { status: response.status, payload }
  } catch (error) {
    return { status: 500, payload: { error: String(error) } }
  }
})

app.whenReady().then(() => {
  createWindow()
  createTray()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
