#include <Adafruit_INA228.h>
#include <Arduino.h>
#include <Servo.h>

#include "HX711.h"

const unsigned long EMERGENCY_STOP_TIME = 2000;

const int PIN_TENS_CLK = 2;
const int PIN_TENS_DATA = 3;
const long LOADCELL_DIVIDER = 175000.0;

const int INA228_I2CADDR = 69;
const double INA228_SHUNT_RESISTANCE = 0.0002;
const double INA228_MAX_CURRENT = 204.8;

const int PWM_PIN = 9;

int pwmTime = 0;
unsigned long lastMessageTime = 0;

Adafruit_INA228 ina228 = Adafruit_INA228();
HX711 tens;

Servo esc;

void sendReading();
void updatePwm(int _pwmTime);

void setup() {
    Serial.begin(115200);
    // Wait until serial port is opened
    while (!Serial) {
        delay(10);
    }

    // Initialize ESC pin
    esc.attach(PWM_PIN);
    esc.writeMicroseconds(1000);

    // setup INA228
    Serial.println("Adafruit INA228 Current Sensor Test");
    if (!ina228.begin(INA228_I2CADDR)) {
        while (1) {
            Serial.println("Could not find INA228 chip. Restart MCU.");
            delay(1000);
        }
    }
    ina228.setShunt(INA228_SHUNT_RESISTANCE, INA228_MAX_CURRENT);
    ina228.setAveragingCount(INA228_COUNT_16);
    ina228.setVoltageConversionTime(INA228_TIME_150_us);
    ina228.setCurrentConversionTime(INA228_TIME_280_us);
    Serial.println("Found INA228 chip");

    // setup HX711
    Serial.println("HX711 Scale Test");
    tens.begin(PIN_TENS_DATA, PIN_TENS_CLK);
    tens.set_scale(LOADCELL_DIVIDER);

    if (!tens.wait_ready_timeout(1000)) {
        while (1) {
            delay(1000);
            Serial.println("HX711 not found. Restart MCU");
        }
    }

    tens.tare(5);

    Serial.println("Found HX711 chip");

    lastMessageTime = millis();  // Update timer
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        if (command == "get") {
            sendReading();
            lastMessageTime = millis();
        } else if (command.startsWith("set ")) {
            updatePwm(command.substring(4).toInt());
            sendReading();
            lastMessageTime = millis();
        } else {
            Serial.println("Unknown command");
        }
    }

    //  Emergency stop if no message received in EMEGENCY_STOP_TIME
    if (millis() - lastMessageTime > EMERGENCY_STOP_TIME) {
        updatePwm(1000);
    }
}

void sendReading() {
    Serial.println("{\"current\": " + String(ina228.readCurrent()) +
                   ", \"voltage\": " + String(ina228.readBusVoltage()) +
                   ", \"tens\": " + String(tens.get_units(5)) +
                   ", \"pwm\": " + String(pwmTime) + "}");

    //{"current": 0.0, "voltage": 0.0, "tens": 0.0, "pwm": 0}
}

void updatePwm(int _pwmTime) {
    if (_pwmTime < 1000) {
        _pwmTime = 1000;
    } else if (_pwmTime > 2000) {
        _pwmTime = 2000;
    }
    esc.writeMicroseconds(_pwmTime);
    pwmTime = _pwmTime;
}
