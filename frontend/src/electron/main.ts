import {app, BrowserWindow, ipcMain} from 'electron';
import {SerialPort} from "serialport";
import { ReadlineParser } from "@serialport/parser-readline";
import * as path from 'path';
import * as fs from 'fs';
import {defaultSettings, Settings} from './settings.js';
import {validateSettings} from './path_utils.js';


let arduinoSettings: Settings = defaultSettings;

const commands: string[] = [];
let serialPort: SerialPort;
let parser: ReadlineParser;

function loadSettingsFromFile() {
  const settingsPath = path.join(app.getAppPath(), process.env.NODE_ENV == "development" ? ".":"..", "/settings.json");
  try {
    if (fs.existsSync(settingsPath)) {
      const data = fs.readFileSync(settingsPath, 'utf-8');
      const jsonData = JSON.parse(data);

      if (validateSettings(jsonData)) {
        arduinoSettings = jsonData;
      }
    } else {
      console.log('Settings file not found. Creating a new file with default settings.');
      arduinoSettings = defaultSettings;
      saveSettingsToFile();
    }
  } catch (err) {
    console.error('Error loading settings:', err);
    arduinoSettings = defaultSettings;
  }
}


function saveSettingsToFile() {
  try {
    const data = JSON.stringify(arduinoSettings, null, 2);
    fs.writeFileSync(path.join(app.getAppPath(), process.env.NODE_ENV == "development" ? ".":"..", "/settings.json"), data, 'utf-8');
    console.log(data);
    console.log('Settings saved successfully');
  } catch (err) {
    console.error('Error saving settings:', err);
  }
}

const createWindow = () => {
  loadSettingsFromFile();

  const win = new BrowserWindow({
    width: 1920,
    height: 1080,
    webPreferences: {
      preload: path.join(app.getAppPath(), process.env.NODE_ENV == "development" ? ".":"..", "/dist-electron/preload.cjs"),
      nodeIntegration: true,
      contextIsolation: true
    },
  })
  if(process.env.NODE_ENV == "development"){
    win.loadURL('http://localhost:5123')
  }else{
    win.loadURL(path.join(app.getAppPath() + '/dist-react/index.html'));
  }

  serialPort = new SerialPort({
    path: arduinoSettings.serial_port,
    baudRate: arduinoSettings.baud_rate
  });
  parser = serialPort.pipe(new ReadlineParser({ delimiter: "\n" }));


  startBackgroundLoop(win);
  ipcMain.on("send-command", (_, command) => {parseCommand(command)});
  ipcMain.on("change-arduino-port", (_,new_port,new_baud_rate) => changeArduinoPort(new_port,new_baud_rate));
  ipcMain.on("change-save-file", (_,file) => changeSaveFile(file));
}

function changeSaveFile(file: string) {
  console.log("Changing save file to:", file);
  arduinoSettings.csv_file = file;
  saveSettingsToFile();
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
  console.log("Changing port to:", new_port, "with baud rate:", new_baud_rate);
  if (serialPort) {
    serialPort.close((err) => {
      if (err) {
        console.error("Error closing port:", err);
      } else {
        console.log("Port closed successfully");
      }
    });
  }

  serialPort = new SerialPort({
    path: new_port,
    baudRate: new_baud_rate
  });

  parser = serialPort.pipe(new ReadlineParser({ delimiter: "\n" }));
  arduinoSettings.serial_port = new_port;
  arduinoSettings.baud_rate = new_baud_rate;
  saveSettingsToFile();

  console.log("Port changed successfully");
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
  const setCommandRegex = /^set (\d+)$/;
  const match = command.match(setCommandRegex);

  if (command == "get" || command.startsWith("set ")) {
      if (match) {
          const pwmValue = parseInt(match[1]);
          if (pwmValue >= 1000 && pwmValue <= 2000) {
              commands.push(command);
              return true;
          } else {
              return false;
          }
      } else {
          return false;
      }
  }
  if (command == "startTest") {
      startTest();
      return true;
  }
  return false;
}


async function startTest(){
  console.log("Starting test");
  const pwm_step:number = defaultSettings.pwm_step_size;
  const delay:number = defaultSettings.command_delay;
  const max_pwm:number = 2000;
  // const data_log:Array<string> = []

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
