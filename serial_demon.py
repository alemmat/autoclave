from enum import Enum, auto
import os
import serial
from fpdf import FPDF
from datetime import datetime
import time


class States(Enum):
    start_cycle = auto()
    save_data_cycle = auto()
    audit = auto()
    set_time = auto()
    write_log = auto()


class AutoClave:

    def __init__(self):
        self.serial_device = serial.Serial('/dev/ttyAMA0')
        self.line = ""

    def read_serial(self):
        data = self.serial_device.read()
        time.sleep(1)
        data_left = self.serial_device.inWaiting()
        data += self.serial_device.read(data_left)

        return data

    def write_temp_file(self):
        f = open("temp.txt", "a")
        f.write(self.line)
        f.close()
        self.line = ""

    def write_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        f = open("temp.txt", "r")

        for x in f:
            pdf.set_left_margin(2.5)
            pdf.cell( 10, 3, txt=x, ln=1, align='l')

        pdf.output(datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')+".pdf")

    def create_file(self):

        self.delete_temp_file()
        f = open("temp.txt", "x")
        f.close()

    def delete_temp_file(self):

        if os.path.isfile("temp.txt"):
            os.remove("temp.txt")

    def state_machine(self, state):

        serial_data = self.read_serial()
        print("serial_data")
        index = 0

        while len(serial_data) > index:

            if state == States.write_log:

                self.line += chr(serial_data[index])

                if serial_data[index] == 0x0D:
                    print("if serial_data[index] == 0x0D:")
                    print(self.line)
                    self.write_temp_file()
                    state = States.save_data_cycle

            if state == States.start_cycle:

                if serial_data[index] == 0xF1:
                    self.create_file()
                    state = States.save_data_cycle

                if serial_data[index] == 0xF4:
                    state = States.audit

                if serial_data[index] == 0xF8:
                    state = States.set_time

            if state == States.save_data_cycle:

                if serial_data[index] == 0xF2:
                    self.write_pdf()
                    self.delete_temp_file()
                    state = States.start_cycle

                if len(serial_data) > 0:
                    if serial_data[index] == 0xF3:
                        state = States.write_log

            if state == States.audit:
                state = States.start_cycle

            if state == States.set_time:
                state = States.start_cycle

            index = index + 1

        print(len(serial_data))
        print(index)
        print("print(len(serial_data))")
        print("print(index)")

        return state


def run_machine():

    autoclave = AutoClave()

    while True:
        autoclave.state_machine(States.start_cycle)


if __name__ == '__main__':
    run_machine()
