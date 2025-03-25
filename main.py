from time import sleep
import csv
from datetime import datetime
from os import path

from busio import I2C
import adafruit_ads1x15.ads1115 as ads
from adafruit_ads1x15.analog_in import AnalogIn
import Gui
import Multimeter
import Arduino


# Define board and multimeter ports
arduino = Arduino.Arduino()
multimeter = Multimeter.MULTIMETER()

# Initialize the Raspberry Pi I2C interface
# i2c = I2C(SCL, SDA)
i2c = I2C(1, 0)

# Create an ADS1115 object and configure it
ads_module = ads.ADS1115(i2c)
ADS_GAIN = 2  # 2.048V
ads_module.gain = ADS_GAIN
ads_module.data_rate = 32  # data rate(SPS) 1000/32ms each measure

adsReferenceMeasureRaw = AnalogIn(ads_module, ads.P1)
adsMeasureRaw = AnalogIn(ads_module, ads.P0)

# counts how many measures points are connected at same time
MEASUREMENT_POINTS = 2
measurementPointsPins = []

# Define arduino analog pin
ANALOG_PIN = 0
ADC_BITS = 10

for i in range(MEASUREMENT_POINTS):
    measurementPointsPins.append([])
    for j in range(2):
        pin = 22 + j + (i * 2)
        arduino.set_pin_mode_digital_output(pin)
        measurementPointsPins[i].append(pin)
        arduino.digital_write(pin, 0)
sleep(1)  # wait reference voltage to stabilize


arduino.set_oversampling_analog_input(ANALOG_PIN, ADC_BITS)


def write_gui(measurement_point, multimeter_measure_voltage, arduinoMeasureTimestamp) -> None:
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
) -> None:
    date_now = datetime.now()
    csv_name = f"{date_now.year}-{date_now.month}-{date_now.day}.csv"
    output_filename = "outputTest/" + csv_name
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
                ADS_GAIN,
                multimeter_measure_voltage,
            ]
        )

def measure_ads(relays, retry=0):
    try:
        ads_reference_voltage = adsReferenceMeasureRaw.voltage # Calibration for my module
        ads_reference_raw = adsReferenceMeasureRaw.value
        ads_voltage = adsMeasureRaw.voltage # Calibration for my module
        ads_voltage_raw = adsMeasureRaw.value
    except:
        print("Error reading ADS1115")
        if (retry < 3):
            print("Retrying ADS1115 read, try #" + str(retry + 1))
            sleep(3)
            measure_ads(retry + 1)
        arduino.digital_write(relays["relay0"], 0)
        arduino.digital_write(relays["relay1"], 0)
        return {"status": False}
    return {"status": True, "ads_reference_voltage": ads_reference_voltage, "ads_reference_raw": ads_reference_raw, "ads_voltage": ads_voltage, "ads_voltage_raw": ads_voltage_raw}

def measure(measurement_point, frame=None) -> bool:
    relay0 = measurementPointsPins[measurement_point][0]
    relay1 = measurementPointsPins[measurement_point][1]
    arduino.digital_write(relay0, 1)
    arduino.digital_write(relay1, 1)
    sleep(1.5)  # 1500ms wait to stabilize voltage
    # try:
    #     ads_reference_voltage = adsReferenceMeasureRaw.voltage + 0.0162 # Calibration for my module
    #     ads_reference_raw = adsReferenceMeasureRaw.value
    #     ads_voltage = adsMeasureRaw.voltage + 0.0162 # Calibration for my module
    #     ads_voltage_raw = adsMeasureRaw.value
    # except:
    #     print("Error reading ADS1115")
    #     arduino.digital_write(relay0, 0)
    #     arduino.digital_write(relay1, 0)
    #     return False
    ADS_measure = measure_ads(relays={"relay0": relay0, "relay": relay0})
    if (ADS_measure["status"] is True):
        ads_reference_voltage = ADS_measure["ads_reference_voltage"]
        ads_reference_raw = ADS_measure["ads_reference_raw"]
        ads_voltage = ADS_measure["ads_voltage"]
        ads_voltage_raw = ADS_measure["ads_voltage_raw"]
    else:
        print("ADS1115 error, using default values")
        ads_reference_voltage = 1.1 # Voltage that Arduino should use as reference
        ads_reference_raw = 0
        ads_voltage = None
        ads_voltage_raw = None
    multimeter_measure = multimeter.read_VDC_value()
    arduino_measure, arduinoMeasureTimestamp = arduino.read_oversampling_value()
 #   multimeter_measure = 0
    if (multimeter_measure["status"] is True):
        multimeter_measure_voltage = multimeter_measure["value"]
    else:
        print("Multimeter error, using default value")
        multimeter_measure_voltage = 0
        # arduino.digital_write(relay0, 0)
        # arduino.digital_write(relay1, 0)
        # return False
    arduino.digital_write(relay0, 0)
    arduino.digital_write(relay1, 0)
#    arduino_measure_voltage = arduino.calc_oversampling_voltage(arduino_measure, ads_reference_voltage)
    arduino_measure_voltage = arduino.calc_oversampling_voltage(arduino_measure,1.096) 
    #arduino_measure_voltage = arduino.calc_oversampling_voltage(arduino_measure, 1.065)
    print(
        f"[{arduinoMeasureTimestamp}] {int(measurement_point + 1)}: "
        f"(Arduino: {arduino_measure:04d}  {arduino_measure_voltage:.4f}V) "
        f"(ads Reference: {ads_reference_raw:05d}  {ads_reference_voltage:.18f}V) "
        f"(ads: {ads_voltage_raw:05d}  {ads_voltage:.18f}V) "
        f"(Diff arduino: {multimeter_measure_voltage - arduino_measure_voltage:.6f}V) "
        f"(Diff ADS: {multimeter_measure_voltage - ads_voltage:.6f}V) "
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
    write_gui(measurement_point + 1,
              '{:.6f}'.format(multimeter_measure_voltage), arduinoMeasureTimestamp)
    if frame:
        frame.append_text(
            f"[{arduinoMeasureTimestamp}] {int(measurement_point + 1)}: "
            f"(Arduino: {arduino_measure:04d}  {arduino_measure_voltage:.4f}V) "
            f"(ads Reference: {ads_reference_raw:05d}  {ads_reference_voltage:.18f}V) "
            f"(ads: {ads_voltage_raw:05d}  {ads_voltage:.18f}V) "
            f"(Multimeter: {multimeter_measure_voltage:.6f}V)\n"
        )
    return True


def measure_all(frame=None) -> None:
    for point in range(MEASUREMENT_POINTS):
        measure_success = measure(point, frame)
        if not measure_success:
            print("Retrying in 3 seconds")
            sleep(3)  # retry in 3 seconds
            measure_success = measure(point, frame)
            if not measure_success:
                return
        sleep(0.25)  # Wait 250ms between each measure
    print("\n")


def manual_measure() -> None:
    frame = gui.FRAME()
    measure_all(frame)
    frame.destroy_frame()


def run() -> None:
    """Measure all points every 60 seconds"""
    gui.after(60000, run)
    measure_all()


if __name__ == "__main__":
    gui = Gui.GUI(manual_measure, MEASUREMENT_POINTS)
    try:
        gui.after(100, run)
        gui.mainloop()
    except KeyboardInterrupt:
        arduino.shutdown()
        i2c.deinit()
        multimeter.close()
        gui.destroy()
        print("Exiting...")
        exit(0)
