import sys
import serial
import json
import time
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QTextEdit, QLineEdit, QLabel, QHBoxLayout, QTabWidget,
    QFormLayout, QMessageBox
)
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import re

class ArduinoGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = {
            "serial_port": "COM3",
            "baud_rate": 115200,
            "pwm_step_size": 500,
            "command_delay": 0.9,
            "serial_connection_wait": 3,
            "csv_file": "test_log.csv"
        }

        self.ser = None
        self.is_connected = False
        self.init_ui()

        self.load_settings()

        self.find_arduino_port()
        self.connect_to_arduino()

    def init_ui(self):
        self.setWindowTitle("Arduino Control Panel")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
         
        self.control_tab = QWidget()
        self.settings_tab = QWidget()
        
        self.tabs.addTab(self.control_tab, "Control Panel")
        self.tabs.addTab(self.settings_tab, "Settings")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.init_control_tab()

        self.init_settings_tab()

    def init_settings_tab(self):
        layout = QFormLayout()

        self.serial_port_input = QLineEdit(self.settings["serial_port"])

        com_regex = QRegularExpression(r"^COM[1-9]\d*$") 
        com_validator = QRegularExpressionValidator(com_regex)
        self.serial_port_input.setValidator(com_validator)

        self.baud_rate_input = QLineEdit(str(self.settings["baud_rate"]))
        self.pwm_step_size_input = QLineEdit(str(self.settings["pwm_step_size"]))
        self.command_delay_input = QLineEdit(str(self.settings["command_delay"]))
        self.serial_connection_wait_input = QLineEdit(str(self.settings["serial_connection_wait"]))
        self.csv_file_input = QLineEdit(self.settings["csv_file"])

        layout.addRow("Serial Port", self.serial_port_input)
        layout.addRow("Baud Rate", self.baud_rate_input)
        layout.addRow("PWM Step Size", self.pwm_step_size_input)
        layout.addRow("Command Delay", self.command_delay_input)
        layout.addRow("Serial Connection Wait", self.serial_connection_wait_input)
        layout.addRow("CSV File", self.csv_file_input)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        self.settings_tab.setLayout(layout)
        
    def init_control_tab(self):
        layout = QVBoxLayout()
        
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output_box)
        
        self.pwm_input = QLineEdit()
        self.pwm_input.setPlaceholderText("Enter PWM value")
        self.pwm_input.setMinimumSize(300, 50)
        self.pwm_input.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.pwm_input)
        
        btn_layout = QHBoxLayout()
        
        self.start_test_btn = QPushButton("Start Test")
        self.start_test_btn.clicked.connect(self.start_test)
        self.start_test_btn.setFixedSize(200, 60)
        self.start_test_btn.setStyleSheet("font-size: 18px;")
        btn_layout.addWidget(self.start_test_btn)
        
        self.set_pwm_btn = QPushButton("Set PWM")
        self.set_pwm_btn.clicked.connect(self.set_pwm)
        self.set_pwm_btn.setFixedSize(200, 60)
        self.set_pwm_btn.setStyleSheet("font-size: 18px;")
        btn_layout.addWidget(self.set_pwm_btn)
        
        self.get_data_btn = QPushButton("Get Data")
        self.get_data_btn.clicked.connect(self.get_data)
        self.get_data_btn.setFixedSize(200, 60)
        self.get_data_btn.setStyleSheet("font-size: 18px;")
        btn_layout.addWidget(self.get_data_btn)
        
        self.make_graphs_btn = QPushButton("Generate Graphs")
        self.make_graphs_btn.clicked.connect(self.generate_graphs)
        self.make_graphs_btn.setFixedSize(200, 60)
        self.make_graphs_btn.setStyleSheet("font-size: 18px;")
        btn_layout.addWidget(self.make_graphs_btn)
        
        layout.addLayout(btn_layout)
        self.control_tab.setLayout(layout)


    def load_settings(self):
        try:
            with open("settings.txt", "r") as file:
                for line in file.readlines():
                    key, value = line.strip().split("=")
                    if key in self.settings:
                        if key == "serial_port":
                            com_regex = r"^COM[1-9]\d*$"
                            if re.match(com_regex, value):
                                self.settings[key] = value
                            else:
                                self.settings[key] = "COM3" 
                        
                        elif key in ["baud_rate", "pwm_step_size", "serial_connection_wait"]:
                            self.settings[key] = int(float(value)) 
                        elif key == "command_delay":
                            self.settings[key] = float(value)
                        else:
                            self.settings[key] = value

                self.serial_port_input.setText(self.settings["serial_port"])
                self.baud_rate_input.setText(str(self.settings["baud_rate"]))  
                self.pwm_step_size_input.setText(str(self.settings["pwm_step_size"]))  
                self.command_delay_input.setText(str(self.settings["command_delay"]))  
                self.serial_connection_wait_input.setText(str(self.settings["serial_connection_wait"]))  
                self.csv_file_input.setText(self.settings["csv_file"])

        except FileNotFoundError:
            self.log_output("Settings file not found. Using default settings.")
        except Exception as e:
            self.log_output(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            self.settings["serial_port"] = self.serial_port_input.text()
            self.settings["baud_rate"] = int(float(self.baud_rate_input.text()))  
            self.settings["pwm_step_size"] = int(self.pwm_step_size_input.text())
            self.settings["command_delay"] = float(self.command_delay_input.text())
            self.settings["serial_connection_wait"] = int(float(self.serial_connection_wait_input.text()))  
            self.settings["csv_file"] = self.csv_file_input.text()

            with open("settings.txt", "w") as file:
                for key, value in self.settings.items():
                    file.write(f"{key}={value}\n")

            self.log_output("Settings saved successfully.")
            
            QMessageBox.information(self, "Success", "Settings have been saved successfully.")
        except ValueError as e:
            self.log_output(f"Error saving settings: {e}. Please ensure all fields have valid values.")
            
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}. Please ensure all fields have valid values.")

    def log_output(self, message):
        self.output_box.append(message)

    def find_arduino_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "Arduino" in port.description:
                self.settings["serial_port"] = port.device
                return port.device
        return None

    def connect_to_arduino(self):
        
        if self.ser and self.ser.is_open:
            self.log_output("Arduino is already connected.")
            self.is_connected = True
            return

        try:
            self.ser = serial.Serial(
                self.settings["serial_port"], 
                self.settings["baud_rate"], 
                timeout=float(self.settings["serial_connection_wait"])
            )
            time.sleep(self.settings["serial_connection_wait"])
            self.is_connected = True
            self.log_output(f"Connected to Arduino on {self.settings['serial_port']}")
            self.ser.reset_input_buffer()
        except serial.SerialException:
            self.is_connected = False
            self.log_output("Failed to connect to Arduino!")

    def start_test(self):
        if not self.is_connected:
            self.log_output("Arduino not connected. Please check the connection.")
            return

        pwm_step = self.settings["pwm_step_size"]
        delay = float(self.settings["command_delay"])
        max_pwm = 2000
        data_log = []

        self.log_output("Starting test...")
        QCoreApplication.processEvents()

        for pwm in range(1000, max_pwm + 1, pwm_step):
            self.log_output(f"Setting PWM to {pwm}")
            QCoreApplication.processEvents()

            self.ser.write(f"set {pwm}\n".encode())
            time.sleep(delay)

            self.ser.write(b"get\n")
            time.sleep(delay)
            
            response = self.ser.readline().decode().strip()
            self.log_output(f"Received response: {response}")
            QCoreApplication.processEvents()

            try:
                response_data = json.loads(response)
                data_log.append([
                    response_data["pwm"],
                    response_data["voltage"],
                    response_data["current"],
                    response_data["tens"],
                ])
                self.log_output(f"Data saved for PWM {pwm}: Voltage: {response_data['voltage']}, Current: {response_data['current']}, Tens: {response_data['tens']}")
                QCoreApplication.processEvents()
            except Exception as e:
                self.log_output(f"Failed to parse response for PWM {pwm}: {response}, Error: {e}")
                QCoreApplication.processEvents()

        pd.DataFrame(data_log, columns=["PWM", "Voltage", "Current", "Tens"]).to_csv(self.settings["csv_file"], index=False)
        self.log_output("Test completed and saved to CSV")
        QCoreApplication.processEvents()

        self.generate_graphs()

    def set_pwm(self):
        if not self.is_connected:
            self.log_output("Arduino not connected. Please check the connection.")
            return

        pwm_value = self.pwm_input.text().strip()
        if pwm_value.isdigit():
            command = f"set {pwm_value}\n"
            self.ser.write(command.encode())
            response = self.ser.readline().decode().strip()
            self.log_output(f"Set PWM to {pwm_value}, Response: {response}")
        else:
            self.log_output("Invalid PWM value")

    def get_data(self):
        if not self.is_connected:
            self.log_output("Arduino not connected. Please check the connection.")
            return

        self.ser.write(b"get\n")
        response = self.ser.readline().decode().strip()
        self.log_output(f"Arduino: {response}")

    def generate_graphs(self):
        if not self.is_connected:
            self.log_output("Arduino not connected. Please check the connection.")
            return

        try:
            data = pd.read_csv(self.settings["csv_file"])
            data["Power"] = (data["Voltage"] * data["Current"]) / 1000000
            
            plt.figure(figsize=(12, 8))
            plt.plot(data["PWM"], data["Power"], marker="o", label="PWM vs Power", color="blue")
            plt.xlabel("PWM")
            plt.ylabel("Power (W)")
            plt.grid(True)
            plt.legend()
            plt.show()
            
            plt.figure(figsize=(12, 8))
            plt.plot(data["PWM"], data["Tens"], marker="o", label="PWM vs Tens", color="green")
            plt.xlabel("PWM")
            plt.ylabel("Tens")
            plt.grid(True)
            plt.legend()
            plt.show()
            
            plt.figure(figsize=(12, 8))
            plt.plot(data["Power"], data["Tens"], marker="o", label="Power vs Tens", color="red")
            plt.xlabel("Power (W)")
            plt.ylabel("Tens")
            plt.grid(True)
            plt.legend()
            plt.show()
            
            self.log_output("Graphs generated successfully")
        except Exception as e:
            self.log_output(f"Error generating graphs: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ArduinoGUI()
    gui.show()
    sys.exit(app.exec())
