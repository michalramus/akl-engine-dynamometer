#include <Adafruit_INA228.h>
#include <Arduino.h>

#include "HX711.h"

const int EMERGENCY_STOP_TIME = 1000;

const int PIN_TENS_CLK = 3;
const int PIN_TENS_DATA = 2;
const long LOADCELL_OFFSET = 50682624;
const long LOADCELL_DIVIDER = 5895655;

const int INA228_I2CADDR = 69;
const double INA228_SHUNT_RESISTANCE = 0.0002;
const double INA228_MAX_CURRENT = 204.8;

const int PWM_PIN = 9;

int pwm = 0;
unsigned int lastMessageTime = 0;

Adafruit_INA228 ina228 = Adafruit_INA228();
HX711 tens;

void sendReading();

void setup() {
    Serial.begin(115200);
    // Wait until serial port is opened
    while (!Serial) {
        delay(10);
    }

    // setup INA228
    if (!ina228.begin(INA228_I2CADDR)) {
        Serial.println("Couldn't find INA228 chip");
        while (1);
    }
    ina228.setShunt(INA228_SHUNT_RESISTANCE, INA228_MAX_CURRENT);
    ina228.setAveragingCount(INA228_COUNT_16);
    ina228.setVoltageConversionTime(INA228_TIME_150_us);
    ina228.setCurrentConversionTime(INA228_TIME_280_us);

    // setup HX711
    tens.begin(PIN_TENS_DATA, PIN_TENS_CLK);
    tens.set_scale(LOADCELL_DIVIDER);
    tens.set_offset(LOADCELL_OFFSET);

    if (!tens.wait_ready_timeout(1000)) {
        Serial.println("HX711 not found.");
        while (1);
    }

    lastMessageTime = millis();  // Update timer
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        if (command == "get") {
            lastMessageTime = millis();
            sendReading();
        } else if (command.startsWith("set ")) {
            pwm = command.substring(4).toInt();
            if (pwm < 0) {
                pwm = 0;
            } else if (pwm > 255) {
                pwm = 255;
            }
            sendReading();
            lastMessageTime = millis();
        }
    }

    //  Emergency stop if no message received in EMEGENCY_STOP_TIME
    if (millis() - lastMessageTime > EMERGENCY_STOP_TIME) {
        pwm = 0;
    }

    //  Update PWM every 100ms
    if (millis() % 100 == 0) {
        analogWrite(PWM_PIN, pwm);
    }
}

void sendReading() {
    Serial.println("{\"current\": " + String(ina228.readCurrent()) +
                   ", \"voltage\": " + String(ina228.readBusVoltage()) +
                   ", \"tens\": " + String(tens.get_units(5)) +
                   ", \"pwm\": " + String(pwm) + "}\n");

    //{"current": 0.0, "voltage": 0.0, "tens": 0.0, "pwm": 0}
}
