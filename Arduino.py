"""apoioColetaDeDados arduino module"""

from time import strftime, localtime, time, sleep
from sys import stderr
import serial.tools.list_ports
from telemetrix import telemetrix

class Arduino(telemetrix.Telemetrix):

    ADC_measures = 0
    ADC_sum = 0
    ADC_measure = -1
    ADC_timestamp = 0

    def __init__(self):
        super().__init__(com_port = self._detect_port(), arduino_wait = 5)


    def _detect_port(self) -> str:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "USB" in port.hwid and "erial" in port.description:
                return port.device
            elif "ttyACM" in port.description:
                return port.device
        print("Arduino not found with \"serial\" in the description.", file=stderr)
        exit(1)

    def set_oversampling_analog_input(self, pin, ADC_bits) -> None:
      self.ADC_bits = ADC_bits - 10
      self.set_analog_scan_interval(0)
      self.set_pin_mode_analog_input(pin, callback=self._oversampling)

    def _oversampling(self, data) -> None:
        self.ADC_measures += 1
        self.ADC_sum += data[2]
        if self.ADC_measures == 4**self.ADC_bits or self.ADC_bits == 0:
            self.ADC_measure = self.ADC_sum
            self.ADC_timestamp = int(data[3])
            self.ADC_measures = 0
            self.ADC_sum = 0

    def set_analog_input(self, pin) -> None:
        self.set_analog_scan_interval(0)
        self.set_pin_mode_analog_input(pin, differential=0, callback=self._ADC)

    def _ADC(self, data) -> None:
        if len(data) < 3:
            print(f"Warning: incomplete ADC data received: {data}")
            return
        self.ADC_measure = data[2]
        self.ADC_timestamp = int(data[3])
        self.ADC_measures = 0
        self.ADC_sum = 0

    def read_oversampling_value(self):
        self.ADC_measures = 0
        self.ADC_sum = 0
        self.ADC_timestamp = 0
        while (self.ADC_timestamp == 0):
            sleep(0.001)
            pass
        return self.ADC_measure, strftime("%Y-%m-%d %H:%M:%S", localtime(self.ADC_timestamp))

    def calc_oversampling_voltage(self, measure, reference_voltage) -> float:
        bits = self.ADC_bits
        return round((measure / 2**bits * reference_voltage) / (4**bits*1023/2**bits), 4)

    def read_ADC_value(self):
        return self.ADC_measure, strftime("%Y-%m-%d %H:%M:%S", localtime(self.ADC_timestamp))

    def calc_ADC_voltage(self, measure, reference_voltage) -> float:
        return round((measure * reference_voltage) / 1023, 4)

