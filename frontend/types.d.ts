export {};

declare global {
  interface Window {
    electron: {
      onArduinoData: (callback: (data: string) => void) => void;
      sendCommand: (command: string) => void;
      changeArduinoPort: (serial_port: string, baud_rate: string) => void;
      changeSaveFile: (file: string) => void;
    };
  }
}
