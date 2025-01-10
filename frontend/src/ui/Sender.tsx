import './Sender.css';
import React from 'react';

interface SenderProps {
  setInputValue: (command: string) => void;
}

const Sender: React.FC<SenderProps> = ({ setInputValue }) => {
  const handleChangeCommand = () => {
    const input = document.getElementById('command-input') as HTMLInputElement;
    if (input) {
      const command = input.value;
      setInputValue(command);
      input.value = '';
    }
  };

  const handleStartTest = () => {
    const command = 'startTest';
    console.log(command);
    setInputValue(command);
  };

  const handleGet = () => {
    const command = 'get';
    setInputValue(command);
  };

  const handleEnter = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleChangeCommand();
    }
  };

  return (
    <div className="sender">
      <h2>Sender</h2>
      <button id="start-test" onClick={handleStartTest}>Start Test</button>
      <button id="send-get" onClick={handleGet}>Get</button>
      <input
        id="command-input"
        type="text"
        placeholder="Enter command here"
        onKeyDown={handleEnter}
      />
      <button id="send-command" onClick={handleChangeCommand}>Send command</button>
    </div>
  );
};

export default Sender;