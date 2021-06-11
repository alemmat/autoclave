#ser = serial.Serial('/dev/ttyACM0')  # open serial port
#print(ser.name)         # check which port was really used
#ser.write(b'hello')     # write a string
#ser.close()

from enum import Enum, auto
import os
import serial

class States(Enum):
    start_cycle = auto()
    save_data_cycle = auto()
    audit = auto()
    set_time = auto()


def init_serial():
    return serial.Serial('/dev/ttyACM0')

def read_serial(serial_device):
    tdata = serial_device.read()           # Wait forever for anything
    time.sleep(1)              # Sleep (or inWaiting() doesn't give the correct value)
    data_left = serial_device.inWaiting()  # Get the number of characters ready to be read
    tdata += serial_device.read(data_left)
    print(tdata)




def set_time():
    array1 = bytearray(b'\xF8')
    array1.extend(b'\x11\x22\x33')
    print(array1)
    #os.system('hwclock --set %s' % date_str)


def state_machine(state, serial_data):

    if state == States.start_cycle:

        if c == 0xF1:
            state = States.save_data_cycle

        if c == 0xF4:
            state = States.audit

        if c == 0xF8:
            state = States.set_time

    if state == States.save_data_cycle:

        if c == 0xF2:
            state = States.start_cycle

        if c == 0xF3:
            state = States.save_data_cycle

    if state == States.audit:
        state = States.start_cycle

    if state == States.set_time:
        set_time()
        state = States.start_cycle

    return state


def run_machine():

    state = States.start_cycle
    serial_port = init_serial()

    while True:

        state = state_machine(state)



if __name__ == '__main__':
    #state_machine()
    serial_device = init_serial()
    read_serial(serial_device)
