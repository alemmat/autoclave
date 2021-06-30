from enum import Enum, auto
import os
import serial
from fpdf import FPDF
from datetime import datetime
import time



class AutoClave:

	serial_device = None

	def __init__(self):
		serial_device = serial.Serial('/dev/ttyAMA0')


	class States(Enum):
	    start_cycle = auto()
	    save_data_cycle = auto()
	    audit = auto()
	    set_time = auto()
	    write_log = auto()

	def read_serial():
	    data = serial_device.read()
	    time.sleep(10)
	    data_left = serial_device.inWaiting()
	    data += serial_device.read(data_left)
	    print(data)


	def write_file(log):

	    f = open("temp.txt", "a")
	    f.write(log)
	    f.close()

	    pdf = FPDF()
	    pdf.add_page()
	    pdf.set_font("Arial", size = 10)

	    f = open("temp.txt", "r")

	    for x in f:
	        pdf.cell(200, 5, txt = x, ln = 1, align = 'C')

	    pdf.output(datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'))

	def create_file():
	    f = open("temp.txt", "x")
	    f.close()

	def state_machine(state, serial_data):

	    index = 0

	    while len(serial_data) > 0:

	        if state == States.start_cycle:

	            if serial_data[index] == 0xF1:
	                serial_data.pop(index)
	                create_file()
	                state = States.save_data_cycle

	            if serial_data[index] == 0xF4:
	                state = States.audit

	            if serial_data[index] == 0xF8:
	                state = States.set_time

	        if state == States.save_data_cycle:

	            if serial_data[index] == 0xF2:
	                serial_data.pop(index)
	                os.remove("temp.txt")
	                state = States.start_cycle

	            if len(serial_data) > 0:
	                if serial_data[index] == 0xF3:
	                    serial_data.pop(index)
	                    state = States.write_log

	        if state == States.write_log:

	            log+=chr(serial_data[index])

	            if serial_data[index] == 0x0D:
	                print(log)
	                write_file(log)
	                state = States.save_data_cycle
	                log=""

	            serial_data.pop(index)

	        if state == States.audit:
	            state = States.start_cycle

	        if state == States.set_time:
	            state = States.start_cycle

	    return state

def run_machine():

	autoclave = AutoClave()
	autoclave.read_serial()


if __name__ == '__main__':
    run_machine()
