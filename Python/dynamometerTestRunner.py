import pandas as pd
import matplotlib.pyplot as plt
import serial
import json
import time
import csv
import os


# Read settings from config file
def read_settings(filename="settings.txt"):
    settings = {
        "serial_port": "COM3",
        "baud_rate": 115200,
        "pwm_step_size": 5,
        "command_delay": 0.3,
        "serial_connection_wait": 2,
        "csv_file": "test_log.csv"
    }
    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                key, value = line.strip().split("=")
                if key in settings:
                    settings[key] = int(value) if value.isdigit() else value
    return settings

# Save data to a CSV file
def save_to_csv(filename, data):
    file_existed = not os.path.exists(filename)
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if file_existed:
            writer.writerow(["PWM", "Current", "Tens"])
        writer.writerows(data)

# Plot graphs from the loggeed data (from file)
def generate_graphs(csv_file):
    try:
        data = pd.read_csv(csv_file)
        required_columns = ["PWM", "Current", "Tens"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"CSV file must contain the following columns: {required_columns}")

        # Plot PWM vs Current
        plt.figure(figsize=(10, 6))
        plt.plot(data["PWM"], data["Current"], marker='o', label="PWM vs Current", color="blue")
        plt.title("PWM vs Current")
        plt.xlabel("PWM")
        plt.ylabel("Current (A)")
        plt.grid(True)
        plt.legend()
        plt.savefig("PWM_vs_Current.png")
        plt.show()

        # Plot PWM vs Tens
        plt.figure(figsize=(10, 6))
        plt.plot(data["PWM"], data["Tens"], marker='o', label="PWM vs Tens", color="green")
        plt.title("PWM vs Tens")
        plt.xlabel("PWM")
        plt.ylabel("Tens")
        plt.grid(True)
        plt.legend()
        plt.savefig("PWM_vs_Tens.png")
        plt.show()

        # Plot Current vs Tens
        plt.figure(figsize=(10, 6))
        plt.plot(data["Current"], data["Tens"], marker='o', label="Current vs Tens", color="red")
        plt.title("Current vs Tens")
        plt.xlabel("Current (A)")
        plt.ylabel("Tens")
        plt.grid(True)
        plt.legend()
        plt.savefig("Current_vs_Tens.png")
        plt.show()

        print("Graphs generated and saved as PNG files.")

    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Conduct the test and log results to CSV
def start_test(ser, settings):
    pwm_step = settings["pwm_step_size"]
    delay = settings["command_delay"]
    max_pwm = 255
    data_log = []

    for pwm in range(0, max_pwm + 1, pwm_step):
        # Set PWM
        command = f"set {pwm}\n"
        ser.write(command.encode())
        time.sleep(delay)

        # Get result
        ser.write(b"get\n")
        response = ser.readline().decode().strip()
        print(f"requested PWM: {pwm}, Response: {response}")

        # Parse and add data to log
        try:
            response_data = json.loads(response)
            data_log.append([pwm, response_data["current"], response_data["tens"]])
        except Exception as e:
            print(f"Failed to parse response: {response}, Error: {e}")

    # Save results to CSV
    save_to_csv(settings["csv_file"], data_log)
    print(f"Test completed. Results saved to {settings['csv_file']}")

def communicate_with_arduino(settings):
    try:
        ser = serial.Serial(settings["serial_port"], settings["baud_rate"], timeout=1)
        time.sleep(settings["serial_connection_wait"])
        print(f"Connected to Arduino on {settings['serial_port']}")

        while True:
            command = input("Enter a command from: startTest, set <pwm>, get, quit ").strip()
            if command == "quit":
                break
            elif command == "startTest":
                start_test(ser, settings)
            elif command.startswith("set "):
                ser.write((command + "\n").encode())
                response = ser.readline().decode().strip()
                print(f"Arduino: {response}")
            elif command == "get":
                ser.write((command + "\n").encode())
                response = ser.readline().decode().strip()
                print(f"Arduino: {response}")
            else:
                print("Unknown command. Try again.")
    except Exception as e:
        print("There was an error in the main loop, likely serial connection issue, see details below: \n")
        print(e)
    finally:
        if ser.is_open:
            ser.close()
        print("Connection closed.")



if __name__ == "__main__":
    settings = read_settings()
    communicate_with_arduino(settings)
