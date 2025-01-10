import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
    sendCommand: (command: string) => {
      ipcRenderer.send('send-command', command);
      console.log(command); 
    },
    onArduinoData: (callback: (data: string) => void) => {
      ipcRenderer.on('arduino-data', (_, data) => callback(data));
    },
    changeArduinoPort: (new_port: string, new_baud_rate: number) => {
      ipcRenderer.send('arduino-data', new_port, new_baud_rate);
    },
    changeSaveFile: (file: string) => {
      ipcRenderer.send('change-save-file',file);
    },
  });