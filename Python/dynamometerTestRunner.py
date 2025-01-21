import pandas as pd
import matplotlib.pyplot as plt
import serial
import json
import time
import csv
import os
import traceback

# Globals
settings = {}
ser = None


# Read settings from config file
def read_settings(filename="settings.txt"):
    global settings
    settings = {
        "serial_port": "COM3",
        "baud_rate": 115200,
        "pwm_step_size": 20,
        "command_delay": 0.9,
        "serial_connection_wait": 3,
        "csv_file": "test_log.csv",
    }
    # Change directory to the file's directory if not already there, to read and save files here.
    currentDir = os.getcwd()
    fileDir = os.path.dirname(os.path.realpath(__file__))
    if currentDir != fileDir:
        print("Changing dir from: ", currentDir, " to: ", fileDir)
        os.chdir(fileDir)
    # Read settings from file
    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                if not "=" in line:  # Skip lines without an '=' sign
                    print(
                        f"Skipping line of settings because of incorrect syntax: {line}"
                    )
                    continue
                key, value = line.strip().split("=")
                if key in settings:
                    settings[key] = int(value) if value.isdigit() else value
    return settings


# Save data to a CSV file
def save_to_csv(filename, data):
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["PWM", "Voltage", "Current", "Tens"])
        writer.writerows(data)


# Plot graphs from the loggeed data (from file)
def generate_graphs(csv_file=""):
    global settings
    if csv_file == "":
        csv_file = settings["csv_file"]
    try:

        data = pd.read_csv(csv_file)
        required_columns = ["PWM", "Voltage", "Current", "Tens"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(
                f"CSV file must contain the following columns: {required_columns}"
            )

        data["Power"] = (data["Voltage"] * data["Current"]) / 1000000
        print("Generating graphs, close previous graphs to view the next one...")

        # Plot PWM vs Power
        plt.figure(figsize=(10, 6))
        plt.plot(
            data["PWM"], data["Power"], marker="o", label="PWM vs Power", color="blue"
        )
        plt.title("PWM vs Power")
        plt.xlabel("PWM")
        plt.ylabel("Power (W)")
        plt.grid(True)
        plt.legend()
        plt.savefig("PWM_vs_Power.png")  # Save graph to file
        plt.show()

        # Plot PWM vs Tens
        plt.figure(figsize=(10, 6))
        plt.plot(
            data["PWM"], data["Tens"], marker="o", label="PWM vs Tens", color="green"
        )
        plt.title("PWM vs Tens")
        plt.xlabel("PWM")
        plt.ylabel("Tens")
        plt.grid(True)
        plt.legend()
        plt.savefig("PWM_vs_Tens.png")  # Save graph to file
        plt.show()

        # Plot Power vs Tens
        plt.figure(figsize=(10, 6))
        plt.plot(
            data["Power"], data["Tens"], marker="o", label="Power vs Tens", color="red"
        )
        plt.title("Power vs Tens")
        plt.xlabel("Power (W)")
        plt.ylabel("Tens")
        plt.grid(True)
        plt.legend()
        plt.savefig("Power_vs_Tens.png")  # Save graph to file
        plt.show()

        print("Graphs generated and saved as PNG files.")

    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Conduct the test and log results to CSV
def start_test():
    global settings, ser
    pwm_step = settings["pwm_step_size"]
    delay = float(settings["command_delay"])
    max_pwm = 2000
    data_log = []

    for pwm in range(1000, max_pwm + 1, pwm_step):
        # Set PWM
        command = f"set {pwm}\n"
        ser.write(command.encode())
        time.sleep(delay)

        # Send a message to signal the connection is active
        ser.reset_output_buffer()
        ser.write(b"get\n")
        time.sleep(delay)
        # Get result (after waiting to stabilise)
        ser.reset_input_buffer()
        ser.write(b"get\n")
        response = ser.readline().decode().strip()
        print(f"requested PWM: {pwm}, Response: {response}")

        # Parse and add data to log
        try:
            response_data = json.loads(response)
            data_log.append(
                [
                    response_data["pwm"],
                    response_data["voltage"],
                    response_data["current"],
                    response_data["tens"],
                ]
            )
        except Exception as e:
            print(f"Failed to parse response: {response}, Error: {e}")

    # Save results to CSV
    save_to_csv(settings["csv_file"], data_log)
    print(f"Test completed. Results saved to {settings['csv_file']}")
    generate_graphs(settings["csv_file"])

def find_arduino_port():
    import serial.tools.list_ports
    global settings
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "Arduino" in port.description:
            print(f"Found Arduino on {port.device}")
            settings["serial_port"] = port.device
            return port.device
    return None

def communicate_with_arduino():
    global ser
    try:
        try:
            ser = serial.Serial(settings["serial_port"], settings["baud_rate"], settings["serial_connection_wait"])
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino on {settings['serial_port']}, trying to find automatically...")
            port = find_arduino_port()
            if port is not None:
                ser = serial.Serial(port, settings["baud_rate"], settings["serial_connection_wait"])
            else:
                raise e
        time.sleep(settings["serial_connection_wait"])
        print(f"Connected to Arduino on {settings['serial_port']}")
        ser.reset_input_buffer()

        while True:
            command = input(
                "Enter a command from: startTest, set <pwm>, get, makeGraphs, quit "
            ).strip()
            if command == "quit":
                break
            elif command == "startTest":
                start_test()
            elif command.startswith("set "):
                ser.write((command + "\n").encode())
                ser.reset_input_buffer()
                response = ser.readline().decode().strip()
                print(f"Arduino: {response}")
            elif command == "get":
                ser.write((command + "\n").encode())
                ser.reset_input_buffer()
                response = ser.readline().decode().strip()
                print(f"Arduino: {response}")
            elif command == "makeGraphs":
                print("Generating graphs...")
                generate_graphs(settings["csv_file"])
            else:
                print("Unknown command. Try again.")
    except Exception as e:
        print(
            "There was an error in the main loop, likely serial connection issue, see details below: \n"
        )
        print(e)
        print(traceback.format_exc())
    finally:
        try:
            if ser.is_open:
                ser.close()
            print("Connection closed.")
        except Exception as e:
            pass  # ser could be None or already closed, we are quitting anyway


read_settings()  # always read the settings on file load, avoid having to call it from frontend
if __name__ == "__main__":
    communicate_with_arduino()
