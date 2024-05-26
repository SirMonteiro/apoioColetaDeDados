"""apoioColetaDeDados multimeter module"""

from time import sleep
from sys import stderr
from serial import Serial, PARITY_NONE, STOPBITS_TWO
import serial.tools.list_ports


class MULTIMETER(Serial):

    def __init__(self):
        super().__init__(
            self._detect_port(),
            9600,
            timeout=0,
            parity=PARITY_NONE,
            rtscts=False,
            xonxoff=False,
            dsrdtr=False,
            stopbits=STOPBITS_TWO,
        )

    def _detect_port(self) -> str:
        ports = serial.tools.list_ports.comports()
        desired_hwid = "12EC:2015" # VID:PID of Yokogawa's TY720 Multimeter
        for port in ports:
            if desired_hwid in port.hwid:
                return port.device
        print(f"Port with HWid '{desired_hwid}' not found.", file=stderr)
        exit(1)

    def read_current_value(self) -> str:
        self.write(b"RR,1\r\n")
        sleep(0.2) # wait 200ms to receive multimeter data
        return self.readline().decode("utf-8")

    def read_VDC_value(self) -> dict:
        current = self.read_current_value()
        battery_low = False
        status = True
        try:
            multimeter_measure_voltage = current.split(",")[2].split("VDC")[0][
                1:
            ]
            if "m" in multimeter_measure_voltage:
                multimeter_measure_voltage = round(
                    float(multimeter_measure_voltage[:-1]) / 1000, 6
                )
            else:
                multimeter_measure_voltage = float(multimeter_measure_voltage)

            if "B" in current.split(",")[1]:
                print("Change multimeter battery!")
                battery_low = True

            if multimeter_measure_voltage == 0:
                print("Error: multimeter reading 0V")
                status = False
        except IndexError:
            print("Error reading multimeter")
            status = False
        return {"value": multimeter_measure_voltage, "battery_low": battery_low, "status": status}
