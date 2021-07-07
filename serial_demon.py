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

    send_ready = auto()


class AutoClave:

    def __init__(self):

        self.serial_device = serial.Serial('/dev/ttyAMA0')
        self.state = States.set_time
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
            pdf.cell( 10, 3, txt=x, ln=1, align='l')

        pdf.output(datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')+".pdf")

    def create_file(self):

        self.delete_temp_file()
        f = open("temp.txt", "x")
        f.close()

    def delete_temp_file(self):

        if os.path.isfile("temp.txt"):
            os.remove("temp.txt")

    def config_time(self):
         os.system('sudo date -u --set="%s"' % "Tue Nov 13 15:23:34 PDT 2018")

    def state_machine(self):

        time_byte_array = bytearray()

        index_time = 0

        while True:

            serial_data = self.read_serial()
            index = 0

            while len(serial_data) > index:

                if self.state == States.write_log:

                    self.line += chr(serial_data[index])

                    if serial_data[index] == 0x0D:

                        self.write_temp_file()
                        self.state = States.save_data_cycle

                if self.state == States.start_cycle:

                    if serial_data[index] == 0xF1:

                        self.create_file()
                        self.state = States.save_data_cycle

                    if serial_data[index] == 0xF4:

                        self.state = States.audit

                if self.state == States.save_data_cycle:

                    if serial_data[index] == 0xF2:

                        self.write_pdf()
                        self.delete_temp_file()
                        self.state = States.start_cycle

                    if serial_data[index] == 0xF3:

                        self.state = States.write_log

                if self.state == States.audit:

                    self.state = States.start_cycle

                if self.state == States.set_time:

                    if serial_data[index] == 0xF8:

                        if index_time > 0:
                            time_byte_array.append(serial_data[index])

                        print(time_byte_array)

                        index_time = index_time +1

                        if index_time > 6:

                            index_time = 0
                            config_time()
                            self.state = States.start_cycle



                index = index + 1

def run_machine():

    autoclave = AutoClave()
    autoclave.state_machine()


if __name__ == '__main__':
    run_machine()
