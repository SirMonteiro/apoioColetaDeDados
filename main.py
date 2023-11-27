from time import sleep, strftime, localtime
import csv
from datetime import datetime
from os import path
from threading import Timer
import serial
# from board import SCL, SDA
from busio import I2C
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from telemetrix import telemetrix

# https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


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
# i2c = I2C(SCL, SDA)
i2c = I2C(1, 0)

# Create an ADS1115 object and configure it
ads = ADS.ADS1115(i2c)
ADS_gain = 2  # 2.048V
ads.gain = ADS_gain
ads.data_rate = 128

adsReferenceMeasureRaw = AnalogIn(ads, ADS.P0)
adsMeasureRaw = AnalogIn(ads, ADS.P1)

# counts how many measures points are connected at same time
MEASUREMENT_POINTS = 3
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
sleep(3)  # wait reference voltage to stabilize


def arduino_callback(data):
    global arduinoMeasureRaw
    global arduinoMeasureTimestamp
    arduinoMeasureRaw = data[2]
    arduinoMeasureTimestamp = strftime(
        '%Y-%m-%d %H:%M:%S', localtime(data[3]))


arduino.set_pin_mode_analog_input(
    ANALOG_PIN, differential=0, callback=arduino_callback)

sleep(1)  # wait arduino_callback populates variables first time


def measure(measurementPoint):
    relay0 = measurementPointsPins[measurementPoint][0]
    relay1 = measurementPointsPins[measurementPoint][1]
    arduino.digital_write(relay0, 0)
    arduino.digital_write(relay1, 0)
    sleep(0.250)  # 250ms wait to stabilize voltage
    multimeter.write(b"RR,1\r\n")
    sleep(0.2)  # wait 200ms to receive multimeter data
    multimeterMeasureRaw = multimeter.read(20)
    try:
        adsReferenceVoltage = adsReferenceMeasureRaw.voltage
        adsReferenceRaw = adsReferenceMeasureRaw.value
        adsVoltage = adsMeasureRaw.voltage
        adsVoltageRaw = adsMeasureRaw.value

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
        # multimeterMeasureVoltage = float(multimeterMeasure.split(",")[2].split("VDC")[
        #     0][1:])
        multimeterMeasureVoltage = multimeterMeasure.split(",")[2].split("VDC")[
            0][1:]
        if ("m" in multimeterMeasureVoltage):
            multimeterMeasureVoltage = float(
                multimeterMeasureVoltage.split("m")[0]) / 1000
        else:
            multimeterMeasureVoltage = float(multimeterMeasureVoltage)
        if (multimeterMeasureVoltage == 0):
            return False
    except:
        print("Error reading multimeter")
        arduino.digital_write(relay0, 1)
        arduino.digital_write(relay1, 1)
        return False
    arduinoMeasureVoltage = round(
        (arduinoMeasure * adsReferenceVoltage) / 1024, 4)
    # print(
    #     f'{arduinoMeasureTimestamp} Arduino: {arduinoMeasure} {arduinoMeasureVoltage}V\tMultimeter: {multimeterMeasureVoltage}\tdiff: {round(arduinoMeasureVoltage - float(multimeterMeasureVoltage), 4)}V\tADS: {round(adsVoltage, 4)}V\tdiff: {round(adsVoltage - float(multimeterMeasureVoltage), 4)}\tADS Reference: {round(adsReferenceVoltage, 4)}V')
    print(f'{int(measurementPoint + 1)} {arduinoMeasureTimestamp} Arduino: {arduinoMeasure:04d}  {arduinoMeasureVoltage:.4f}V\tADS Reference: {adsReferenceRaw:05d}  {adsReferenceVoltage:.18f}V\tADS: {adsVoltageRaw:05d}  {adsVoltage:.18f}V\tMultimeter: {multimeterMeasureVoltage:.4f}V')
    date = datetime.now()
    csvName = f"{date.year}-{date.month}-{date.day}.csv"
    if path.exists(f'output/{csvName}'):
        with open(
            f"output/{date.year}-{date.month}-{date.day}.csv",
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
                    adsReferenceRaw,
                    adsReferenceVoltage,
                    adsVoltageRaw,
                    adsVoltage,
                    ADS_gain,
                    multimeterMeasureVoltage
                ]
            )
    else:
        # File does not exist, write header row
        with open(f'output/{csvName}', "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Point", "timeStamp", "Arduino", "ADSReference", "ADSReferenceVoltage",  "ADS", "ADSVoltage", "ADSGain", "Multimeter"])
    return True


def measure_all():
    for i in range(MEASUREMENT_POINTS):
        measureSuccess = measure(i)
        if (not measureSuccess):
            print("Retrying in 10 seconds")
            sleep(10)  # retry in 10 seconds
            measureSuccess = measure(i)
            if (not measureSuccess):
                return
        sleep(0.05)  # Wait 50ms between each measure
    print('\n')


try:
    # Create csv file
    date = datetime.now()
    csvName = f"{date.year}-{date.month}-{date.day}.csv"
    if not path.exists(f'output/{csvName}'):
        with open(f'output/{csvName}', "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Point", "timeStamp", "Arduino", "ADSReference", "ADSReferenceVoltage",  "ADS", "ADSVoltage", "ADSGain", "Multimeter"])
    measure_all()
    RepeatedTimer(60, measure_all)  # measure all points every 60 seconds
except KeyboardInterrupt:
    arduino.shutdown()
    multimeter.close()
