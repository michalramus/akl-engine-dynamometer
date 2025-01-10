import React from 'react';
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
  const handleSetSettings = () => {
    const serial_port = document.getElementById('serial_port') as HTMLInputElement;
    const baud_rate = document.getElementById('baud_rate') as HTMLInputElement;
    const csv_file = document.getElementById('csv_file') as HTMLInputElement;

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
      <button id="apply_settings" onClick={handleSetSettings}>Apply Settings</button>
    </div>
  );
};

export default Settings;
