from enum import Enum, auto
import os
import serial
from datetime import datetime
import time
import requests


class States(Enum):

    start_cycle = auto()
    save_data_cycle = auto()
    set_time = auto()
    write_log = auto()
    send_ready = auto()
    wait_time_config = auto()
    audit = auto()
    cycle = auto()

class AutoClave:

    def __init__(self):

        self.serial_device = serial.Serial('/dev/ttyUSB0')
        self.state = States.wait_time_config
        self.line_url_state = States.audit
        self.line = ""
        self.time_byte_array = bytearray()


        self.ciclo_id = 0
        self.audit_id = 0
        self.localhost = "http://127.0.0.1:5000"

        self.create_new_cycle = "/ciclo/new"
        self.var_insert_line = "/{dir}/{id}/insert"
        self.close_cycle = "/ciclo/{}/close"
        self.var_close_open_cycle = "/ciclo/coc"

        self.create_new_audit = "/audit/new"
        self.var_insert_audit_line = "/audit/insert"
        self.close_audit = "/audit/close"

    def read_serial(self):

        data = self.serial_device.read()
        time.sleep(1)
        data_left = self.serial_device.inWaiting()
        data += self.serial_device.read(data_left)
        return data

    def bcd_to_int(self,bcd):

        final_number = ( ( bcd & 0xF0 ) >> 4 ) * 10
        final_number = final_number + (bcd & 0x0F)

        return final_number

    def config_time(self):

        time = "20{year}{month}{day} {hour}:{minute}:{seconds}"

        now = time.format(
        year = self.bcd_to_int( self.time_byte_array[0] ),
        month = self.bcd_to_int( self.time_byte_array[1] ),
        day = self.bcd_to_int( self.time_byte_array[2] ),
        hour = self.bcd_to_int( self.time_byte_array[3] ),
        minute = self.bcd_to_int( self.time_byte_array[4] ),
        seconds = self.bcd_to_int( self.time_byte_array[5] ) )

        os.system('sudo date --set="%s"' % now)

    def create_audit(self):

        response = requests.get(self.localhost+self.create_new_audit)
        jsonResponse = response.json()
        self.audit_id = jsonResponse["audit_id"]

    def create_ciclo(self):

        response = requests.get(self.localhost+self.create_new_cycle)
        jsonResponse = response.json()
        self.ciclo_id = jsonResponse["ciclo_id"]


    def fun_insert_line(self, url):
        response = requests.post(self.localhost+url, json={'line':self.line})
        jsonResponse = response.json()

        if self.line_url_state == States.audit:
            self.audit_id = jsonResponse["audit_id"]

        if self.line_url_state == States.cycle:
            self.ciclo_id = jsonResponse["ciclo_id"]

        self.line = ""

    def fun_close_cycle(self):
        requests.get(self.localhost+self.close_cycle.format(str(self.ciclo_id)))

    def notify_power_up(self):
        self.serial_device.write(0xF8)
        self.serial_device.write(0xF3)

    def fun_close_open_cycle(self):
        requests.get(self.localhost+self.var_close_open_cycle)

    def fun_close_audit(self):
        requests.get(self.localhost+self.close_audit)

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

                        self.fun_insert_line(self.line_url)
                        self.state = self.previous_state

                if self.state == States.start_cycle:

                    if serial_data[index] == 0xF1:

                        self.create_ciclo()
                        self.state = States.save_data_cycle

                    if serial_data[index] == 0xF4:

                        self.line_url =  self.var_insert_audit_line
                        self.line_url_state = States.audit
                        self.previous_state = States.start_cycle
                        self.state = States.write_log

                    if serial_data[index] == 0xF3:

                        self.create_ciclo()
                        self.line_url = self.var_insert_line.format(dir="ciclo",id=str(self.ciclo_id))
                        self.line_url_state = States.cycle
                        self.previous_state = States.save_data_cycle
                        self.state = States.write_log

                if self.state == States.save_data_cycle:

                    if serial_data[index] == 0xF2:

                        self.fun_close_cycle()
                        self.state = States.start_cycle

                    if serial_data[index] == 0xF3:

                        self.line_url = self.var_insert_line.format(dir="ciclo",id=str(self.ciclo_id))
                        self.line_url_state = States.cycle
                        self.previous_state = States.save_data_cycle
                        self.state = States.write_log

                    if serial_data[index] == 0xF4:

                        self.line_url = self.var_insert_audit_line
                        self.line_url_state = States.audit
                        self.previous_state = States.save_data_cycle
                        self.state = States.write_log

                if self.state == States.wait_time_config:

                    if serial_data[index] == 0xF8:
                        self.state = States.set_time

                if self.state == States.set_time:

                    self.fun_close_open_cycle()

                    if index_time > 0:
                        self.time_byte_array.append(serial_data[index])

                    index_time = index_time +1

                    if index_time > 6:

                        index_time = 0
                        self.config_time()
                        time.sleep(10)

                        self.state = States.start_cycle

                index = index + 1

def run_machine():

    autoclave = AutoClave()
    autoclave.state_machine()


if __name__ == '__main__':
    run_machine()
