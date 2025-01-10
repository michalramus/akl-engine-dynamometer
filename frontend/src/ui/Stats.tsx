import './Stats.css';
import React from 'react';

interface ArduinoData {
  current: number;
  voltage: number;
  tens: number;
  pwm: number;
}

interface StatsProps {
  arduinoData: ArduinoData;
}

const Stats: React.FC<StatsProps> = ({ arduinoData }) => {
  return (
    <div className="stats">
      <h2>Stats</h2>
      <p>current: <span id="thrust-value">{arduinoData.current.toFixed(2)}</span> </p>
      <p>voltage: <span id="humidity-value">{arduinoData.voltage.toFixed(2)}</span> V</p>
      <p>tens: <span id="temperature-value">{arduinoData.tens.toFixed(2)}</span> </p>
      <p>pwm: <span id="voltage-value">{arduinoData.pwm.toFixed(1)}</span> </p>
    </div>
  );
};

export default Stats;