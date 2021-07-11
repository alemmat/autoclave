from enum import Enum, auto
import os
import serial
from datetime import datetime
import time
from PyPDF2 import PdfFileWriter
import sqlite3

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


class States(Enum):

    start_cycle = auto()
    save_data_cycle = auto()
    audit = auto()
    set_time = auto()
    write_log = auto()
    send_ready = auto()
    wait_time_config = auto()

class AutoClave:

    def __init__(self):

        self.serial_device = serial.Serial('/dev/ttyAMA0')
        self.state = States.wait_time_config
        self.line = ""
        self.time_byte_array = bytearray()


    def read_serial(self):

        data = self.serial_device.read()
        time.sleep(1)
        data_left = self.serial_device.inWaiting()
        data += self.serial_device.read(data_left)
        return data

    def write_temp_cycle_file(self):
        self.write_temp_file(file_name="temp_cycle.txt")

    def write_temp_audit_file(self):
        self.write_temp_file(file_name="temp_audit.txt")

    def write_temp_file(self, file_name):

        f = open(file_name, "a")
        f.write(self.line)
        f.close()
        self.line = ""

    def write_audit_pdf(self):
        self.write_pdf(file_name="temp_audit.txt", letter="L")

    def write_cycle_pdf(self):
        self.write_pdf(file_name="temp_cycle.txt", letter="C")

    def write_pdf(self, file_name, letter):

        c = canvas.Canvas("test.pdf")
        f = open(file_name, "r")

        i=0

        for line in f:
            i = i+1
            c.drawString(1 * cm, 29.7 * cm - 1 * cm - i * cm, line.replace('\r','').replace('\n',''))

        c.save()


    def create_temp_cycle_file(self):

        self.delete_temp_cycle_file()
        self.create_temp_file(file_name="temp_cycle.txt")

    def create_temp_audit_file(self):

        self.delete_temp_audit_file()
        self.create_temp_file(file_name="temp_audit.txt")

    def create_temp_file(self,file_name):

        f = open(file_name, "x")
        f.close()

    def delete_temp_cycle_file(self):
        self.delete_temp_file(file_name="temp_cycle.txt")

    def delete_temp_audit_file(self):
        self.delete_temp_file(file_name="temp_audit.txt")

    def delete_temp_file(self,file_name):

        if os.path.isfile(file_name):
            os.remove(file_name)

    def config_time(self):

        print(self.time_byte_array)
        self.create_temp_audit_file()
        os.system('sudo date -u --set="%s"' % "Tue Nov 13 15:23:34 PDT 2018")

    def create_ciclo(self):

        sqlit_insert = "INSERT INTO ciclo (path,date_created,state) VALUES (?,?,?) RETURNING *;"
        data_tuple = ("C"+datetime.utcnow().strftime('%y_%m_%d_%H:%M')+".pdf", datetime.utcnow(), 0)

        con = sqlite3.connect('/home/pi/autoclave/flaskblog/site.db')
        cur = con.cursor()
        result = cur.execute(sqlit_insert,data_tuple)
        print(result)
        con.commit()
        con.close()




    def state_machine(self):

        index_time = 0

        while True:

            serial_data = self.read_serial()
            index = 0
            print(serial_data)

            while len(serial_data) > index:

                if self.state == States.write_log:

                    self.line += chr(serial_data[index])

                    if serial_data[index] == 0x0D:

                        self.write_temp_cycle_file()
                        self.state = States.save_data_cycle

                if self.state == States.start_cycle:

                    if serial_data[index] == 0xF1:

                        self.create_temp_cycle_file()
                        self.create_ciclo()
                        self.state = States.save_data_cycle

                if self.state == States.save_data_cycle:

                    if serial_data[index] == 0xF2:

                        self.write_cycle_pdf()
                        self.delete_temp_cycle_file()
                        self.state = States.start_cycle

                    if serial_data[index] == 0xF3:

                        self.state = States.write_log

                if self.state == States.audit:

                    self.state = States.start_cycle

                if self.state == States.wait_time_config:

                    if serial_data[index] == 0xF8:

                        self.state = States.set_time

                if self.state == States.set_time:

                    if index_time > 0:

                        self.time_byte_array.append(serial_data[index])

                    index_time = index_time +1

                    if index_time > 6:

                        index_time = 0
                        print(serial_data)
                        self.config_time()
                        self.state = States.start_cycle


                index = index + 1

def run_machine():

    autoclave = AutoClave()
    autoclave.state_machine()


if __name__ == '__main__':
    run_machine()
