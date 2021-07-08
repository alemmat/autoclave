from enum import Enum, auto
import os
import serial
from fpdf import FPDF
from datetime import datetime
import time

from flaskblog.models import Ciclo
from flaskblog import db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()
app = Flask(__name__)

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


        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskblog/site.db'
        db.init_app(app)

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

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        f = open(file_name, "r")

        for x in f:
            pdf.cell( 10, 3, txt=x, ln=1, align='l')

        pdf.output(letter+datetime.utcnow().strftime('%y_%m_%d_%H:%M')+".pdf")

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
        os.system('sudo date -u --set="%s"' % "Tue Nov 13 15:23:34 PDT 2018")

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

                        self.ciclo = Ciclo(path="C"+datetime.utcnow().strftime('%y_%m_%d_%H:%M')+".pdf", state=0)
                        db.session.add(self.ciclo)
                        db.session.commit()

                        self.create_temp_cycle_file()
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
