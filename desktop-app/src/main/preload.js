const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close')
});

contextBridge.exposeInMainWorld('api', {
  request: async (endpoint, options = {}) => {
    const baseURL = 'http://localhost:8000';
    const response = await fetch(`${baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    return response.json();
  }
});
