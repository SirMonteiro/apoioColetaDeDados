from time import sleep, strftime, localtime
import csv
from datetime import datetime
from os import path
import serial
from board import SCL, SDA
from busio import I2C
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from telemetrix import telemetrix

# Define board and multimeter ports
arduino = telemetrix.Telemetrix(com_port="/dev/ttyUSB1", arduino_wait=3)
multimeter = serial.Serial(
    "/dev/ttyUSB0",
    9600,
    timeout=0,
    parity=serial.PARITY_NONE,
    rtscts=False,
    xonxoff=False,
    dsrdtr=False,
    stopbits=serial.STOPBITS_TWO,
)

# Initialize the Raspberry Pi I2C interface
i2c = I2C(SCL, SDA)

# Create an ADS1115 object and configure it
ads = ADS.ADS1115(i2c)
ads.gain = 2
ads.data_rate = 128

adsReferenceMeasureRaw = AnalogIn(ads, ADS.P0)
adsMeasureRaw = AnalogIn(ads, ADS.P1)

# counts how many measures points are connected at same time
MEASUREMENT_POINTS = 2
measurementPointsPins = []

# Define arduino analog pin
ANALOG_PIN = 0

for i in range(MEASUREMENT_POINTS):
    measurementPointsPins.append([])
    for j in range(2):
        pin = 22 + j + (i * 2)
        arduino.set_pin_mode_digital_output(pin)
        measurementPointsPins[i].append(pin)
        arduino.digital_write(pin, 1)
sleep(5)  # wait reference voltage to stabilize


def arduino_callback(data):
    global arduinoMeasureRaw
    global arduinoMeasureTimestamp
    arduinoMeasureRaw = data[2]
    arduinoMeasureTimestamp = strftime("%Y-%m-%d %H:%M:%S", localtime(data[3]))


arduino.set_pin_mode_analog_input(ANALOG_PIN, differential=1, callback=arduino_callback)


def measure(measurementPoint):
    relay0 = measurementPointsPins[measurementPoint][0]
    relay1 = measurementPointsPins[measurementPoint][1]
    arduino.digital_write(relay0, 0)
    arduino.digital_write(relay1, 0)
    sleep(0.25)  # 250ms wait to stabilize voltage
    multimeter.write(b"RR,1\r\n")
    sleep(0.15)  # wait 150ms to receive multimeter data
    multimeterMeasureRaw = multimeter.read(20)
    try:
        adsReferenceVoltage = round(adsReferenceMeasureRaw.voltage, 4) + 0.0025
        adsVoltage = round(adsMeasureRaw.voltage, 4) + 0.0025
        adsVoltageRaw = int(adsMeasureRaw.value)
    except:
        print("Error reading ADS1115")
        arduino.digital_write(relay0, 1)
        arduino.digital_write(relay1, 1)
        return False
    arduinoMeasure = int(arduinoMeasureRaw)
    arduino.digital_write(relay0, 1)
    arduino.digital_write(relay1, 1)
    multimeterMeasure = multimeterMeasureRaw.decode("utf-8")
    try:
        multimeterMeasureVoltage = float(
            multimeterMeasure.split(",")[2].split(" VDC")[0][1:]
        )
        if multimeterMeasureVoltage == 0:
            return False
    except:
        print("Error reading multimeter")
        arduino.digital_write(relay0, 1)
        arduino.digital_write(relay1, 1)
        return False
    arduinoMeasureVoltage = round((arduinoMeasure * adsReferenceVoltage) / 1024, 4)
    print(
        f"{arduinoMeasureTimestamp} Arduino: {arduinoMeasure} {arduinoMeasureVoltage}V\tMultimeter: {multimeterMeasureVoltage}\tdiff: {round(arduinoMeasureVoltage - float(multimeterMeasureVoltage), 4)}V\tADS: {round(adsVoltage, 4)}V\tdiff: {round(adsVoltage - float(multimeterMeasureVoltage), 4)}\tADS Reference: {round(adsReferenceVoltage, 4)}V"
    )
    date = datetime.now()
    csvName = f"{date.year}-{date.month}-{date.day}.csv"
    if path.exists(csvName):
        with open(
            f"{date.year}-{date.month}-{date.day}.csv",
            "a",
            encoding="UTF8",
            newline="",
        ) as f:
            writer = csv.writer(f)
            # write the data
            writer.writerow(
                [
                    int(measurementPoint + 1),
                    arduinoMeasureTimestamp,
                    arduinoMeasure,
                    multimeterMeasureVoltage,
                    adsVoltageRaw,
                    round(adsVoltage, 4),
                    adsReferenceVoltage,
                ]
            )
    else:
        # File does not exist, write header row
        with open(csvName, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Point",
                    "timeStamp",
                    "Arduino",
                    "Multimeter",
                    "ADSRaw",
                    "ADS",
                    "ReferenceVoltage",
                ]
            )
    return True


try:
    while True:
        for i in range(MEASUREMENT_POINTS):
            measureSuccess = measure(i)
            if not measureSuccess:
                print("Retrying in 10 seconds")
                sleep(10)  # retry in 10 seconds
                measure(i)
            sleep(0.5)
except KeyboardInterrupt:
    arduino.shutdown()
    multimeter.close()
