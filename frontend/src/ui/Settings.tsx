import React, { useState } from 'react';
import './Settings.css';

interface SettingsData {
  serial_port: string;
  baud_rate: string;
  csv_file: string;
}

interface SettingsSender {
  setInputValue: (settings: SettingsData) => void;
}

const Settings: React.FC<SettingsSender> = ({ setInputValue }) => {
  const [errorMessage, setErrorMessage] = useState<string>('');
  
  const allowedBaudRates = [
    300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, 115200
  ];

  const handleSetSettings = () => {
    const serial_port = document.getElementById('serial_port') as HTMLInputElement;
    const baud_rate = document.getElementById('baud_rate') as HTMLInputElement;
    const csv_file = document.getElementById('csv_file') as HTMLInputElement;

    const serialPortRegex = /^COM\d+$/;
    const csvFileRegex = /^[a-zA-Z0-9_\- ]+\.csv$/;

    if (!serialPortRegex.test(serial_port.value) && serial_port.value !== '') {
      setErrorMessage('Port COM musi mieć format: COM{liczba}');
      return;
    }

    if (!csvFileRegex.test(csv_file.value) && csv_file.value !== '') {
      setErrorMessage('Plik musi mieć rozszerzenie .csv i nie może zawierać specjalnych znaków.');
      return;
    }

    const baudRateValue = parseInt(baud_rate.value);
    if (baud_rate.value !== '' && !allowedBaudRates.includes(baudRateValue)) {
      setErrorMessage('Dozwolone baud rate: 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 31250, 38400, 57600, 115200');
      return;
    }

    setErrorMessage('');
    console.log(serial_port.value);
    console.log(baud_rate.value);
    console.log(csv_file.value);

    setInputValue({
      serial_port: serial_port.value,
      baud_rate: baud_rate.value,
      csv_file: csv_file.value,
    });
  };

  return (
    <div className="settings">
      <h2>Settings</h2>
      <input id="serial_port" type="text" placeholder="Serial Port: COM3" />
      <input id="baud_rate" type="text" placeholder="Baud Rate: 115200" />
      <input id="csv_file" type="text" placeholder="CSV File: test_log.csv" />
      {errorMessage && <div className="error-message">{errorMessage}</div>}
      <button id="apply_settings" onClick={handleSetSettings}>Apply Settings</button>
    </div>
  );
};

export default Settings;
