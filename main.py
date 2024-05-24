from time import sleep, strftime, localtime
import csv
from datetime import datetime
from os import path
import serial

# from board import SCL, SDA
from busio import I2C
import adafruit_ads1x15.ads1115 as ads
from adafruit_ads1x15.analog_in import AnalogIn
from telemetrix import telemetrix
import Gui

# Define board and multimeter ports
arduino = telemetrix.Telemetrix(arduino_wait=3)
multimeter = serial.Serial(
    "/dev/ttyUSB10",
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
ads_module = ads.ADS1115(i2c)
ADS_gain = 2  # 2.048V
ads_module.gain = ADS_gain
ads_module.data_rate = 128

adsReferenceMeasureRaw = AnalogIn(ads_module, ads.P0)
adsMeasureRaw = AnalogIn(ads_module, ads.P1)

# counts how many measures points are connected at same time
MEASUREMENT_POINTS = 3
measurementPointsPins = []

# Define arduino analog pin
ANALOG_PIN = 1
# Define arduino callback global variables
arduinoMeasureRaw = 0
arduinoMeasureTimestamp = ""

for i in range(MEASUREMENT_POINTS):
    measurementPointsPins.append([])
    for j in range(2):
        pin = 22 + j + (i * 2)
        arduino.set_pin_mode_digital_output(pin)
        measurementPointsPins[i].append(pin)
        arduino.digital_write(pin, 1)
sleep(3)  # wait reference voltage to stabilize


def arduino_callback(data)->None:
    global arduinoMeasureRaw
    global arduinoMeasureTimestamp
    arduinoMeasureRaw = data[2]
    arduinoMeasureTimestamp = strftime("%Y-%m-%d %H:%M:%S", localtime(data[3]))


arduino.set_pin_mode_analog_input(
    ANALOG_PIN, differential=0, callback=arduino_callback)

sleep(1)  # wait arduino_callback populates variables first time


def write_gui(measurement_point, multimeter_measure_voltage)->None:
    gui.change_timestamp(arduinoMeasureTimestamp)
    gui.change_measurement(measurement_point, multimeter_measure_voltage)


def write_csv(
    measurement_point,
    arduino_measure_timestamp,
    arduino_measure,
    ads_reference_raw,
    ads_reference_voltage,
    ads_voltage_raw,
    ads_voltage,
    multimeter_measure_voltage,
)->None:
    date_now = datetime.now()
    csv_name = f"{date_now.year}-{date_now.month}-{date_now.day}.csv"
    output_filename = "output/" + csv_name
    if not path.exists(output_filename):
        # File does not exist, write header row
        with open(output_filename, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Point",
                    "timeStamp",
                    "Arduino",
                    "ADSReference",
                    "ADSReferenceVoltage",
                    "ads",
                    "ADSVoltage",
                    "ADSGain",
                    "Multimeter",
                ]
            )
    with open(
        output_filename,
        "a",
        encoding="UTF8",
        newline="",
    ) as f:
        writer = csv.writer(f)
        # write the data
        writer.writerow(
            [
                int(measurement_point + 1),
                arduino_measure_timestamp,
                arduino_measure,
                ads_reference_raw,
                ads_reference_voltage,
                ads_voltage_raw,
                ads_voltage,
                ADS_gain,
                multimeter_measure_voltage,
            ]
        )


def measure(measurement_point, frame=None)->bool:
    relay0 = measurementPointsPins[measurement_point][0]
    relay1 = measurementPointsPins[measurement_point][1]
    arduino.digital_write(relay0, 0)
    arduino.digital_write(relay1, 0)
    sleep(1.25)  # 1250ms wait to stabilize voltage
    multimeter.write(b"RR,1\r\n")
    sleep(2)  # wait 2000ms to receive multimeter data
    multimeter_measure_raw = multimeter.read(20)
    try:
        ads_reference_voltage = adsReferenceMeasureRaw.voltage
        ads_reference_raw = adsReferenceMeasureRaw.value
        ads_voltage = adsMeasureRaw.voltage
        ads_voltage_raw = adsMeasureRaw.value
    except:
        print("Error reading ADS1115")
        arduino.digital_write(relay0, 1)
        arduino.digital_write(relay1, 1)
        return False
    arduino_measure = int(arduinoMeasureRaw)
    arduino.digital_write(relay0, 1)
    arduino.digital_write(relay1, 1)
    multimeter_measure = multimeter_measure_raw.decode("utf-8")
    try:
        # multimeter_measure_voltage = float(multimeter_measure.split(",")[2].split("VDC")[
        #     0][1:])
        multimeter_measure_voltage = multimeter_measure.split(",")[2].split("VDC")[0][
            1:
        ]
        if "m" in multimeter_measure_voltage:
            multimeter_measure_voltage = round(
                float(multimeter_measure_voltage[:-1]) / 1000, 6
            )
        else:
            multimeter_measure_voltage = float(multimeter_measure_voltage)
        if multimeter_measure_voltage == 0:
            print("Error: multimeter reading 0V")
            return False
        if "B" in multimeter_measure.split(",")[1]:
            print("Change multimeter battery!")
    except IndexError:
        print("Error reading multimeter")
        # multimeter_measure_voltage = 0.0000
        return False
    arduino_measure_voltage = round(
        (arduino_measure * ads_reference_voltage) / 1024, 4)

    # print(
    #     f"{arduinoMeasureTimestamp} Arduino: {arduino_measure} {arduino_measure_voltage}V\t"
    #     f"Multimeter: {multimeter_measure_voltage}\t"
    #     f"diff: {round(arduino_measure_voltage - float(multimeter_measure_voltage),4)}V\t"
    #     f"ADS: {round(ads_voltage, 4)}V\t"
    #     f"diff: {round(ads_voltage - float(multimeter_measure_voltage),4)}\t"
    #     f"ADS Reference: {round(ads_reference_voltage, 4)}V"
    # )
    print(
        f"[{arduinoMeasureTimestamp}] {int(measurement_point + 1)}: "
        f"(Arduino: {arduino_measure:04d}  {arduino_measure_voltage:.4f}V) "
        f"(ads Reference: {ads_reference_raw:05d}  {ads_reference_voltage:.18f}V) "
        f"(ads: {ads_voltage_raw:05d}  {ads_voltage:.18f}V) "
        f"(Multimeter: {multimeter_measure_voltage:.6f}V)"
    )
    write_csv(
        measurement_point,
        arduinoMeasureTimestamp,
        arduino_measure,
        ads_reference_raw,
        ads_reference_voltage,
        ads_voltage_raw,
        ads_voltage,
        multimeter_measure_voltage,
    )
    write_gui(measurement_point + 1, '{:.6f}'.format(multimeter_measure_voltage))
    if frame:
        frame.append_text(
            f"[{arduinoMeasureTimestamp}] {int(measurement_point + 1)}: "
            f"(Arduino: {arduino_measure:04d}  {arduino_measure_voltage:.4f}V) "
            f"(ads Reference: {ads_reference_raw:05d}  {ads_reference_voltage:.18f}V) "
            f"(ads: {ads_voltage_raw:05d}  {ads_voltage:.18f}V) "
            f"(Multimeter: {multimeter_measure_voltage:.6f}V)\n"
        )
    return True


def measure_all(frame=None)->None:
    for point in range(MEASUREMENT_POINTS):
        measure_success = measure(point, frame)
        if not measure_success:
            print("Retrying in 5 seconds")
            sleep(5)  # retry in 5 seconds
            measure_success = measure(point, frame)
            if not measure_success:
                return
        sleep(0.25)  # Wait 250ms between each measure
    print("\n")


def manual_measure()->None:
    frame = gui.FRAME()
    measure_all(frame)
    frame.destroy_frame()


def run()->None:
    """Measure all points every 60 seconds"""
    gui.after(60000, run)
    measure_all()


gui = Gui.GUI(manual_measure, MEASUREMENT_POINTS)

try:
    gui.after(100, run)
    gui.mainloop()
except KeyboardInterrupt:
    arduino.shutdown()
    multimeter.close()
    gui.destroy()
    print("Exiting...")
