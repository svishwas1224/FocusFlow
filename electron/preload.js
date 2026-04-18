import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electron', {
  version: process.versions.electron,
  invokeBackend: (method: string, endpoint: string, body?: any) => ipcRenderer.invoke('invoke-backend', method, endpoint, body),
})
