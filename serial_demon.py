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
        self.audit_id = 0
        self.localhost = "http://127.0.0.1:5000"

        self.create_new_cycle = "/ciclo/new"
        self.insert_line = "/{dir}/{id}/insert"
        self.close_cycle = "/ciclo/{}/close"

        self.create_new_audit = "/audit/new"
        self.insert_audit_line = "/audit/{}/insert"
        self.close_audit = "/audit/{}/close"

    def read_serial(self):

        data = self.serial_device.read()
        time.sleep(1)
        data_left = self.serial_device.inWaiting()
        data += self.serial_device.read(data_left)
        return data

    def bcd_to_string(self,bcd):

        string = ( ( bcd & 0xF0 ) >> 4 ) * 10
        string = string + (bcd & 0x0F)

        return string

    def config_time(self):

        time = "20{year}{month}{day} {hour}:{minute}:{seconds}"

        print(time.format( year = self.bcd_to_string( self.time_byte_array[0] ),
        month = self.bcd_to_string( self.time_byte_array[1] ),
        day = self.bcd_to_string( self.time_byte_array[2] ),
        hour = self.bcd_to_string( self.time_byte_array[3] ),
        minute = self.bcd_to_string( self.time_byte_array[4] ),
        seconds = self.bcd_to_string( self.time_byte_array[5] ) ) )


        #os.system('sudo date -u --set="%s"' % "Tue Nov 13 15:23:34 PDT 2018")

    def create_audit(self):

        response = requests.get(self.localhost+self.create_new_audit)
        jsonResponse = response.json()
        self.audit_id = jsonResponse["audit_id"]

    def create_ciclo(self):

        response = requests.get(self.localhost+self.create_new_cycle)
        jsonResponse = response.json()
        self.ciclo_id = jsonResponse["ciclo_id"]


    def l_insert(self, line):
        response = requests.post(self.localhost+line, json={'line':self.line})
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

                        self.l_insert(self.line_url)
                        self.state = self.previous_state

                if self.state == States.start_cycle:

                    if serial_data[index] == 0xF1:

                        self.create_ciclo()
                        self.state = States.save_data_cycle

                    if serial_data[index] == 0xF4:

                        self.line_url = self.insert_line.format(dir="audit",id=str(self.audit_id))
                        self.previous_state = States.start_cycle
                        self.state = States.write_log

                    if serial_data[index] == 0xF3:

                        self.create_ciclo()
                        self.line_url = self.insert_line.format(dir="ciclo",id=str(self.ciclo_id))
                        self.previous_state = States.save_data_cycle
                        self.state = States.write_log

                if self.state == States.save_data_cycle:

                    if serial_data[index] == 0xF2:

                        self.c_cycle()
                        self.state = States.start_cycle

                    if serial_data[index] == 0xF3:

                        self.line_url = self.insert_line.format(dir="ciclo",id=str(self.ciclo_id))
                        self.previous_state = States.save_data_cycle
                        self.state = States.write_log

                    if serial_data[index] == 0xF4:

                        self.line_url = self.insert_line.format(dir="audit",id=str(self.audit_id))
                        self.previous_state = States.save_data_cycle
                        self.state = States.write_log


                if self.state == States.wait_time_config:

                    if serial_data[index] == 0xF8:

                        self.state = States.set_time

                if self.state == States.set_time:

                    if index_time > 0:

                        self.time_byte_array.append(serial_data[index])

                    index_time = index_time +1

                    if index_time > 6:

                        index_time = 0
                        self.config_time()
                        self.create_audit()
                        self.state = States.start_cycle

                index = index + 1

def run_machine():

    autoclave = AutoClave()
    autoclave.state_machine()


if __name__ == '__main__':
    run_machine()
