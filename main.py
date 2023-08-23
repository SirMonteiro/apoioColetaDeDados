from datetime import datetime
from time import sleep
from os import path
import csv
import pyfirmata
import serial

# Define board and multimeter ports
arduino = pyfirmata.ArduinoMega("/dev/ttyUSB0")
multimeter = serial.Serial(
    "/dev/ttyUSB1",
    9600,
    timeout=0,
    parity=serial.PARITY_NONE,
    rtscts=False,
    xonxoff=False,
    dsrdtr=False,
    stopbits=serial.STOPBITS_TWO,
)

# Start iterator
it = pyfirmata.util.Iterator(arduino)  # type: ignore
it.start()

# counts how many measures points are connected at same time
measurementPoints = 2
measurementPointsPins = []

# Define pins
analogPin0 = arduino.get_pin("a:0:i")

for i in range(measurementPoints):
    measurementPointsPins.append([])
    for j in range(2):
        measurementPointsPins[i].append(
            arduino.get_pin("d:" + str(22 + j + (i * 2)) + ":o")
        )
        measurementPointsPins[i][j].write(1)
sleep(1)

# loop
while True:
    for i in range(measurementPoints):
        measurementPointsPins[i][0].write(0)
        measurementPointsPins[i][1].write(0)
        sleep(0.25)
        multimeter.write(b"RR,1\r\n")
        sleep(0.1)
        arduinoMeasure = analogPin0.read()
        multimeterMeasure = multimeter.read(20)
        measurementPointsPins[i][0].write(1)
        measurementPointsPins[i][1].write(1)
        if len(multimeterMeasure) < 15:
            print("Error")
            continue
        # print "b'RR,N,+0.4033 VDCA\\r\\n'" to 0.4033
        multimeterMeasure = multimeterMeasure.decode("utf-8")
        multimeterMeasure = multimeterMeasure.split("+")[1].split(" ")[0]
        arduinoMeasure = round(arduinoMeasure * 1.0658 / 1023, 4)
        measureDiff = round(arduinoMeasure - float(multimeterMeasure), 4)
        print(
            "Arduino: "
            + str(arduinoMeasure)
            + "V Multimeter: "
            + str(multimeterMeasure)
            + "V diff "
            + str(measureDiff)
            + " V"
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
                        arduinoMeasure,
                        multimeterMeasure,
                        measureDiff,
                    ]
                )
        else:
            # File does not exist, write header row
            with open(csvName, "w", encoding="UTF8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Arduino", "Multimeter", "Diff"])
        sleep(0.1)


arduino.exit()
multimeter.close()
