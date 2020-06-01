# ************************************************************
# File:     cmdex_serial.py
# Version:  1.1.12 (01 Jun 2020)
# Author:   Asst.Prof.Dr.Santi Nuratch
#           Embedded Computing and Control Laboratory
#           ECC-Lab, INC, KMUTT, Thailand
# Update:   08:21:28, 01 Jun 2020
# ************************************************************
# 
# 
# Copyright 2020 Asst.Prof.Dr.Santi Nuratch
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 



"""
************************************************************
* File:    CmdexSerial.py                                  *
* Author:  Asst.Prof.Dr.Santi Nuratch                      *
*          Embedded Computing and Control Laboratory       *
*          ECC-Lab, INC, KMUTT, Thailand                   *
* Update:  22 May 2020                                     *
************************************************************
"""

import serial
import time
from serial.tools import list_ports

class CmdexSerial:

    def __init__(self, port, baudrate=115200, **kwargs):


        # Port name (string)
        self._port = port # string, e.g., COM1, COM2, ...

        # Boudrate
        self._boudrate = baudrate

        # Timeout
        self._timeout = 1/200

        # Serial port object
        self._uart = None

        # Port objects. (.device and .description)
        self._ports = []

        # Initialises and open the serial port
        self.port_init()

    def port_init(self):

        err = False
        try:
            # If the serial object is created and opened, close it
            if self._uart != None:
                # Close the port
                if self._uart.isOpen():
                    self._uart.closed()
                    self._uart = None

            # Initialise and open the serial port


            # print('\t--> port_init()')

            self._uart = serial.Serial(port=self._port, baudrate=self._boudrate,timeout=self._timeout)

            '''
            When the port open the MCU is reset, because the RTS and DTR are activated!
            '''
            ''' Required for PIC24 board '''
            self._uart.rts = None
            self._uart.dtr = None
            time.sleep(2)
            self._uart.flushInput()
            self._uart.flushOutput()
            self._uart.read()

            print(f'CmdexSerial: Opening port {self._port}...')
            # time.sleep(2)




            if not self._uart.isOpen():
                self._uart.open()

            # Check if the port is opened
            if not self._uart.isOpen():
                raise # Raise the error, activate the exception (see below)

        except Exception as e:
            # if False: print(f'Could not open the port "{self._port}"')
            print(f'CmdexSerial: Exception at CmdexSerial.port_init -> {e}')
            err = True
        finally:
            if not err:
                print(f'CmdexSerial: {self._uart.port} [{self._uart.baudrate}-N-8-1]')
            return not err


    def port_open(self, port, baudrate):
        self._port     = port
        self._boudrate = baudrate
        return self.port_init()

    def port_close(self):
        if not self._uart.isOpen():
            self._uart.close()
            self._uart = None
        return True

    def port_is_open(self):
        return self._uart and self._uart.isOpen()

    def port_write(self, data):
        err = False
        try:
            if self._uart.isOpen():

                if type(data) != bytearray:
                    self._uart.write(bytearray(data, 'utf-8'))
                else:
                    self._uart.write(data)
            else:
                raise
        except Exception as e:
            print(f'CmdexSerial: Exception at CmdexSerial.write -> {e}')
            err = True
        finally:
            return not err

    def port_write_bytes(self, bytes_data):
        return self.port_write(bytes_data)

    def port_write_string(self, string_data):
        return self._uart.port_write(string_data)

    def port_write_command(self, cmdex_cmd):
        cmd = cmdex_cmd
        if type(cmd) != bytearray:
            cmd = bytearray(cmd, 'utf-8')
        cmd = cmd.split(b'\r')[0] + b'\r\n'
        return self.port_write(cmd)


    def port_enumerate(self):
        """
        Prints device (port name) and description of the ports found in the system.
        """
        self._ports = list_ports.comports()
        print("\n".join([
            port.device + ': ' + port.description
            for port in self._ports
        ]))


    def port_get_ports(self):
        """
        Returns port objects found in the system. Each port object contains `.device` and `.description`.
        """
        self._ports = list_ports.comports()
        return self._ports


    def port_get_names(self):
        """
        Returns port names found in the system, e.g., COM1, COM2,...
        """
        self._ports = self.port_get_ports()
        names = [] # COM1,COM2,..
        for port in self._ports:
            names.append(port.device)
        return names
