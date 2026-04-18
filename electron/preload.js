const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  version: process.versions.electron,
  invokeBackend: (method, endpoint, body) => ipcRenderer.invoke('invoke-backend', method, endpoint, body),
})
