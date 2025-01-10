import React, { useEffect, useState } from 'react';
import reactLogo from './assets/react.svg';
import './App.css';
import Terminal from './Terminal';
import Settings from './Settings';
import Sender from './Sender';
import Stats from './Stats';
import Charts from './Charts';
import { ipcRenderer } from 'electron';
import { SerialPort } from 'serialport';

interface ArduinoData {
  current: number;
  voltage: number;
  tens: number;
  pwm: number;
}

const App: React.FC = () => {
  const [arduinoData, setArduinoData] = useState<ArduinoData>({
    current: 0,
    voltage: 0,
    tens: 0,
    pwm: 0,
  });
  const [commands, setCommands] = useState<string[]>([]);

  const validateArduinoData = (data: string): ArduinoData | null => {
    try {
      const parsedData: Partial<ArduinoData> = JSON.parse(data);
      if (
        typeof parsedData.current === 'number' &&
        typeof parsedData.voltage === 'number' &&
        typeof parsedData.tens === 'number' &&
        typeof parsedData.pwm === 'number'
      ) {
        return parsedData as ArduinoData;
      } else {
        console.warn('Invalid data structure:', parsedData);
        return null;
      }
    } catch (error) {
      console.error('Failed to parse JSON:', error);
      return null;
    }
  };

  useEffect(() => {
    const handleArduinoData = (data: string) => {
      const validData = validateArduinoData(data);
      if (validData) {
        setArduinoData(validData);
      } else {
        console.warn('Using last valid data.');
      }
    };

    window.electron.onArduinoData(handleArduinoData);

    return () => {
      window.electron.onArduinoData(() => {});
    };
  }, []);

  const addCommand = (newCommand: string): void => {
    if (newCommand.trim()) {
      console.log('Adding command:', newCommand);
      window.electron.sendCommand(newCommand); // Sending data to Arduino
      setCommands((prevCommands) => [...prevCommands, newCommand]);
    }
  };

  const setSettings = ({ serial_port, baud_rate, csv_file }: { serial_port: string; baud_rate: string; csv_file: string }): void => {
    if(serial_port != "" && baud_rate != ""){
      window.electron.changeSaveFile(serial_port,baud_rate);
    }
    if(csv_file != ""){
      window.electron.changeSaveFile(csv_file);
    }
  }

  return (
    <div className='main_container'>
      <div className="left-panel">
        <>
          {<Settings setInputValue={setSettings} />}
          {/* <Settings /> */}
          <Terminal commands={commands} />
        </>
      </div>
      <div className="right-panel">
        <>
          <Sender setInputValue={addCommand} />
          <Stats arduinoData={arduinoData} />
          <Charts />
        </>
      </div>
    </div>
  );
};

export default App;
