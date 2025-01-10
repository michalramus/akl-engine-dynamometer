import './Terminal.css';
import React, { useEffect, useRef } from 'react';

interface TerminalProps {
  commands?: string[];
}

const Terminal: React.FC<TerminalProps> = ({ commands = [] }) => {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const terminal = terminalRef.current;
    if (terminal) {
      terminal.scrollTop = terminal.scrollHeight;
    }
  }, [commands]);

  return (
    <div className="terminal_container">
      <h2>Output Terminal</h2>
      <div className="terminal" ref={terminalRef}>
        <div>Welcome to hamownia shell!</div>
        {/* <div>Type --help to get more info about commands</div> */}
        {commands.map((command, index) => (
          <div key={index}>&gt; {command}</div>
        ))}
        <div>~$</div>
      </div>
    </div>
  );
};

export default Terminal;
