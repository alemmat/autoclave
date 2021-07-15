from enum import Enum, auto
import os
import serial
from datetime import datetime
import time
import sqlite3
import requests


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
        self.path = '/home/pi/autoclave/flaskblog/static/ciclos/'

        self.ciclo_id = 0
        self.localhost = "http://127.0.0.1:5000"
        self.create_new_cycle = "/ciclo/new"
        self.insert_line = "/ciclo/{}/insert"
        self.close_cycle = "/ciclo/{}/close"


    def read_serial(self):

        data = self.serial_device.read()
        time.sleep(1)
        data_left = self.serial_device.inWaiting()
        data += self.serial_device.read(data_left)
        return data

    def config_time(self):

        print(self.time_byte_array)
        os.system('sudo date -u --set="%s"' % "Tue Nov 13 15:23:34 PDT 2018")

    def create_ciclo(self):

        response = requests.get(self.localhost+self.create_new_cycle)
        jsonResponse = response.json()
        self.ciclo_id = jsonResponse["ciclo_id"]

    def l_insert(self):
        response = requests.post(self.localhost+self.insert_line.format(str(self.ciclo_id)), json={'line':self.line})
        self.line = ""

    def c_cycle(self):
        requests.get(self.localhost+self.close_cycle.format(str(self.ciclo_id)))

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

                        self.l_insert()
                        self.state = States.save_data_cycle

                if self.state == States.start_cycle:

                    if serial_data[index] == 0xF1:

                        self.create_ciclo()

                        self.state = States.save_data_cycle

                if self.state == States.save_data_cycle:

                    if serial_data[index] == 0xF2:

                        self.c_cycle()
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
