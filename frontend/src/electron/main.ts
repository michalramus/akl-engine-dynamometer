import {app, BrowserWindow, ipcMain} from 'electron';
import {SerialPort} from "serialport";
import { ReadlineParser } from "@serialport/parser-readline";
import * as path from 'path';

interface Settings {
    serial_port: string;
    baud_rate: number;
    pwm_step_size: number;
    command_delay: number;
    serial_connection_wait: number;
    csv_file: string;
}
 
const defaultSettings: Settings = {
    serial_port: "COM11",
    baud_rate: 115200,
    pwm_step_size: 5,
    command_delay: 30,
    serial_connection_wait: 3,
    csv_file: "test_log.csv",
};


const commands: string[] = [];
let serialPort: SerialPort = new SerialPort({
    path: defaultSettings.serial_port,
    baudRate: defaultSettings.baud_rate
  });
let parser : ReadlineParser = serialPort.pipe(new ReadlineParser({ delimiter: "\n" }));



const createWindow = () => {
  const win = new BrowserWindow({
    width: 1920,
    height: 1080,
    webPreferences: {
      preload: path.join(app.getAppPath(), process.env.NODE_ENV == "development" ? ".":",", "/dist-electron/preload.cjs"),
      nodeIntegration: true,
      contextIsolation: true
    },
  })
  if(process.env.NODE_ENV == "development"){
    win.loadURL('http://localhost:5123')
  }else{
    win.loadURL(path.join(app.getAppPath() + '/dist-react/index.html'));
  }
  startBackgroundLoop(win);
  ipcMain.on("send-command", (_, command) => {parseCommand(command)});
  ipcMain.on("change-arduino-port", (_,new_port,new_baud_rate) => changeArduinoPort(new_port,new_baud_rate));
  ipcMain.on("change-save-file", (_,file) => changeSaveFile(file));
}

function changeSaveFile(file: string) {
  defaultSettings.csv_file = file;
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

function changeArduinoPort(new_port:string, new_baud_rate:number) {
    serialPort = new SerialPort({
        path:new_port,
        baudRate: new_baud_rate
      });
    parser = serialPort.pipe(new ReadlineParser({ delimiter: "\n" }));
}

function startBackgroundLoop(win: BrowserWindow) {
  setInterval(() => {
    if (commands.length > 0) {
      const command = commands.shift();
      if (command) {
        serialPort.write(`${command}\n`);
      }
    }
  }, 50);

  parser.on("data", (data:string) => {
    console.log("Received from Arduino:", data);

    if (win) {
        win.webContents.send("arduino-data", data);
    }
  });
}

function parseCommand(command: string): boolean {
    if(command == "get" || command.startsWith("set ")) {
        commands.push(command);
        return true;
    }
    if(command == "startTest"){
      console.log("Starting test");
      startTest();
    }
    return false;
}

async function startTest(){
  console.log("Starting test");
  const pwm_step:number = defaultSettings.pwm_step_size;
  const delay:number = defaultSettings.command_delay;
  const max_pwm:number = 2000;
  const data_log:Array<string> = []

  for (let pwm = 1000; pwm <= max_pwm; pwm += pwm_step) {
    // Set PWM
    const command = `set ${pwm}`;
    commands.push(command);
    await sleep(delay);
    // Get result
    commands.push("get");
    console.log(command);

    // Idk it has to be here
    // parser.on("data", (data:string) => {
    //   data_log.push(command + " " + data);
    // })

  }
  // TODO save to csv 
  // TODO print

}

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
