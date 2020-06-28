"""
#************************************************************
#* File:    CmdexCore.py                                   *
#* Author:  Asst.Prof.Dr.Santi Nuratch                      *
#*          Embedded Computing and Control Laboratory       *
#*          ECC-Lab, INC, KMUTT, Thailand                   *
#* Update:  22 May 2020                                     *
#************************************************************
"""

from PyCmdex.cmdex_serial import *

import threading
import time
import keyboard
import uuid
from datetime import datetime

import serial
from serial.tools import list_ports

import webbrowser
import sys

class CmdexCore(CmdexSerial):

    def __init__(self, port=None, baudrate=115200, **kwargs):




        self._line_callback    = None
        self._adc_callback     = None
        self._psw_callback     = None
        self._led_callback     = None
        self._timeout_callback = None

        self._debug_core = False

        self._exit_keys = ['ctrl+up','ctrl+down']





        # Arguments processing

        # Exit key
        if 'exit_key' in kwargs:
            self._exit_keys.clear()
            self._exit_keys.append(kwargs['exit_key'])

        if 'debug_core' in kwargs:
            self._debug_core = kwargs['debug_core']

        # If the port is None, the auto-detection is performed.
        if port == None:
            port = self.handshake()

        #
        super().__init__(port, baudrate, **kwargs)

        self.__callbacks = {}


        # The last pair of cmmmand-callback
        self._last_cmd_cbk  = {'cmd':None,'cbk':None}

        # List of cmmmand-callback pairs
        self._queue_cmd_cbk = []

        # Thread
        self._thread = None

        # Running flag of the worker thread
        self._thread_running = False

        # Get the thread Daemon. If the daemon is True, the core-thread will be terminated when the main program ends
        self._thread_daemon = False;
        if 'daemon' in kwargs:
            is_demon = kwargs['daemon']
            if is_demon == True or is_demon == False:
                self._thread_daemon = is_demon

        # Response waiting flag
        self._cmdex_waiting = False

        # Waiting counter
        self._waiting_counter = 0
        self._retry_counter = 0


        #
        # Update callbacks passed through the kwqrgs
        #

        # Cmdex formatted Line received callback
        if 'line_callback' in kwargs:
            self._line_callback = kwargs['line_callback']

        # ADC event line received
        if 'adc_callback' in kwargs:
            self._adc_callback = kwargs['adc_callback']

        # PSW event line received
        if 'psw_callback' in kwargs:
            self._psw_callback = kwargs['psw_callback']

        # LED event line received
        if 'led_callback' in kwargs:
            self._led_callback = kwargs['led_callback']

        # Timeout callback
        if 'timeout_callback' in kwargs:
            self._timeout_callback = kwargs['timeout_callback']



        self.__interval_objects = {}

        self._interval_thread   = None

        self.__timeout_objects  = {}


        # Start
        self.start()


    def get_date_time(self):
        return str(datetime.now())

    def get_date(self):
        sp = str(datetime.now()).split(' ')
        return sp[0] # yyyy-mm-dd

    def get_time(self):
        sp = str(datetime.now()).split(' ')
        return sp[1] # hh:mm:ss.xxxxxx

    def handshake(self):
        """
        Performs handshaking.
        If the MCU is detected, returns the port name, otherwise returns None.
        """

        print("\r\nCmdexCore: Serial port detecting...")

        # Get port names, e.g., COM1, COM2,...
        port_names = self.port_get_names()
        if len(port_names) > 0:
            s = 's' if len(port_names) > 1 else ''
            print(f'  Found {len(port_names)} port{s}:')
            for p_name in port_names:
                print('    - ' + p_name)
        else:
            print(f"CmdexCore: No port is found!")



        target_port = None

        # Open and perform handshake
        for p_name in port_names:
            try:
                # Open the port
                print(f"CmdexCore: Performs handshaking @ {p_name}...")

                _uart = CmdexSerial(port=p_name, baudrate=115200,timeout=1)._uart
                # _uart = ser._uart

                if _uart.isOpen():
                    # Sends a request to MCU
                    _uart.write(b'ver,0\r\n')

                    loop_flag = True
                    retry_count = 0
                    while loop_flag == True:

                        line = _uart.readline()

                        # Check if the MCU responds on the  port.
                        if len(line) > 0:
                            sp = line.split(b',')
                            # print(sp)
                            if sp[0] == b'ok: ver':
                                print(f'CmdexCore: MCU is detected @ {p_name}')
                                ver = ""
                                ver = ver.join(map(chr, sp[-1]))
                                print(f'\r\nMCUFirmware: {ver}')
                                loop_flag = False
                                target_port = p_name
                                retry_count = 99
                                break # Breaks while
                        else:
                            if target_port == None:
                                print(f'CmdexCore: Performs handshaking [{retry_count}/10]')
                                _uart.read()
                                _uart.write(b'ver,0\r\n')
                                retry_count += 1
                                if retry_count > 10:
                                    print(f'CmdexCore: MCU is not found @ {p_name}')
                                    break

                    # Breaks for
                    if target_port != None:
                        break

            except Exception as e:
                print(f'CmdexCore: Exception --> {e}')
            finally:
                _uart.close()
                pass

        # print('CmdexCore: Handshake ended')
        return target_port


    def stop(self):
        """ Stops the core-thread and closes the port """
        self._thread_running = False    # Stop the worker thread
        return self.port_close()        # Close the port


    def start(self):
        """ Starts the core-thread of the Cmdex """
        if not self.port_is_open():
            return False

        # Create and start the worker thread
        self._thread_running = True
        self._thread = threading.Thread(None, self.__worker, 'worker', daemon=self._thread_daemon)
        self._thread.start()
        return True


    def split_cmdex_params(self, line_bytes):
        """ Splits the Cmdex-formated line, delimited by comma, into a list """
        sp1 = sp2 = b''
        try:
            sp1 = sp2 = b''
            sp1 = line_bytes.replace(b'\r\n',b'').replace(b' ',b'')
            sp1 = sp1.split(b',')
            sp2 = sp1[0].split(b':')
        except Exception as e:
            print(f'CmdexCore Exception -> {e}')
        return sp2+sp1[1:]


    def is_cmdex_format(self, line_bytes):
        """ Returns True if the given line is the Cmdex-formated """
        s = line_bytes
        return (s.startswith(b"ok: ") or s.startswith(b"err: ")) and s.endswith(b"\r\n")


    def is_cmdex_ok(self, line_bytes):
        """ Returns True if the given line is the ok-line of the Cmdex-formated """
        s = line_bytes
        return s.startswith(b"ok: ") and self.is_cmdex_format(line_bytes)


    def is_cmdex_err(self, line_bytes):
        """ Returns True if the given line is the err-line of the Cmdex-formated """
        s = line_bytes
        return s.startswith(b"err: ") and self.is_cmdex_format(line_bytes)


    def add_callback(self, type, callback):
        """
        Adds a callback function into the callback dictionary

            - type: event name, e.g., "line", "psw", "adc", "led".
            - callback: callback function.
        """

        if type in self.__callbacks:
            cbk = self.__callbacks.pop(type)
            cbk = cbk + [callback]
            self.__callbacks.update({type:cbk})
        else:
            self.__callbacks.update({type:[callback]})


    # Private method. This method is executed by the thread created in the start().
    def __worker(self):

        # Print exit-key information
        s = ""
        i = 0
        for k in self._exit_keys:
            s += "\"" + k.upper() + "\""
            i += 1
            if i < len(self._exit_keys):
                s += " or "
        print(f'CmdexCore: Service is running....\r\nCmdexCore: Press {s} to exit.')


        # Thread sleep time
        __sleep_time = 1/50

        while True:

            try:

                time.sleep(__sleep_time)

                # Check the ending keys or running flag
                need_exit = False
                for k in self._exit_keys:
                    if keyboard.is_pressed(k):
                        need_exit = True
                        break

                if need_exit or self._thread_running == False:
                    self.stop()
                    self._thread_running = False
                    break

                # Check the port. If the port is closed, end the service
                if not self._uart.isOpen():
                    print(f'CmdexCore: The port "{self._uart.port}" is closed. The Cmdex service is stopped.')
                    self._thread_running = False
                    continue


                # Make a request to the Cmdex running in the MCU side
                if self._cmdex_waiting == False and len(self._queue_cmd_cbk) > 0:

                    # Takes the command and callback
                    self._last_cmd_cbk = self._queue_cmd_cbk.pop(0)

                    # Set the waiting flag
                    self._cmdex_waiting   = True

                    # Clear waiting counter
                    self._waiting_counter = 0
                    self._retry_counter = 0

                    # Sends the command to MCU
                    self.port_write_bytes(self._last_cmd_cbk['cmd'])
                    if self._debug_core == True:
                        cmd = self._last_cmd_cbk['cmd'].replace('\r\n', '');
                        print(f'{self.get_date_time()} CmdexCore: Write command {cmd} to MCU')



                # Waiting for the Cmdex response message
                # A command is sent to the MCU. Waiting for response message
                if self._cmdex_waiting == True:

                    self._waiting_counter += 1

                    if self._waiting_counter >=  0.05/__sleep_time:# 0.25/__sleep_time:

                        # Timeout!

                        # Reset the waiting counter
                        self._waiting_counter = 0


                        ##
                        # Retrying operation
                        ##
                        self._retry_counter += 1
                        if self._retry_counter >= 3:
                            self._retry_counter = 0     # Reset retry-counter
                            self._cmdex_waiting = False # Reset waiting-flag

                            # Print
                            if self._debug_core == True:
                                cmd = self._last_cmd_cbk['cmd'].replace('\r\n', '');
                                print(f'{self.get_date_time()} CmdexCore: command {cmd} failed!')
                        else:
                            # Retry
                            self.port_write_bytes(self._last_cmd_cbk['cmd'])

                            # Print
                            if self._debug_core == True:
                                cmd = self._last_cmd_cbk['cmd'].replace('\r\n', '');
                                print(f'{self.get_date_time()} CmdexCore: Timeout @ {cmd}, retry [{self._retry_counter}/3]')




                        # Report timeout
                        # Performs the timeout callback
                        if self._timeout_callback != None:
                            self._timeout_callback([b'timeout'] + self.split_cmdex_params(self._last_cmd_cbk['cmd']))

                        # Perform callback if required
                        if self._last_cmd_cbk['cbk'] != None:
                            # Performs the callback
                            self._last_cmd_cbk['cbk']( [b'timeout'] + self.split_cmdex_params(self._last_cmd_cbk['cmd']) )

                        # If no callbacks, print the timeout information to the console
                        if self._timeout_callback == None and self._last_cmd_cbk['cbk'] != None:
                            print('CmdexCore: ' + 'Timeout @ {}, do callback!'.format( str(self._last_cmd_cbk['cmd']).replace('\r\n','') ))



                # Read data
                line_bytes = self._uart.readline()
                if len(line_bytes) > 0:

                    # Got a new line, performs the callback
                    self.__line_processor(line_bytes)

                    # Perform callbacks added by the add_callback()
                    for key in self.__callbacks:

                        if key == 'line':
                            for cbk in self.__callbacks[key]:
                                cbk(line_bytes)

                        elif key == 'psw' and line_bytes.find(b'psw,') > 2 and self.is_cmdex_format(line_bytes):
                            for cbk in self.__callbacks[key]:
                                cbk(line_bytes)

                        elif key == 'adc' and line_bytes.find(b'adc,') > 2 and self.is_cmdex_format(line_bytes):
                            for cbk in self.__callbacks[key]:
                                cbk(line_bytes)

                        elif key == 'led' and line_bytes.find(b'led,') > 2 and self.is_cmdex_format(line_bytes):
                            for cbk in self.__callbacks[key]:
                                cbk(line_bytes)

            except Exception as e:
                print(f'CmdexCore: Exception -> {e}')




    # Private method. This method is executed by the __worker().
    def __line_processor(self, line_bytes):

        try:

            resp_type = 'res' # or evt

            # Cmdex Format checking
            if (line_bytes.startswith(b'ok: ') or line_bytes.startswith(b'err: ')) and line_bytes.endswith(b'\r\n'):

                sp1 = sp2 = b''

                # Remove the \r\n and space
                sp1 = line_bytes.replace(b'\r\n',b'').replace(b' ',b'')

                # Split
                sp1 = sp1.split(b',')

                # Format checking
                if len(sp1) >= 1:
                    sp2 = sp1[0].split(b':')

                if len(sp2) >= 1:

                    # callback data
                    cbk_data = sp2+sp1[1:]

                    # cmdex formated line received callback
                    if self._line_callback != None:
                        self._line_callback(cbk_data)


                    # ADC event line received callback
                    if self._adc_callback != None:
                        if cbk_data[1] == b'adc' and len(cbk_data) == 6: # ok, adc, id, value, delta, dir
                            resp_type = 'evt'
                            self._adc_callback(cbk_data)


                    # PSW event line received callback
                    if self._psw_callback != None:
                        if cbk_data[1] == b'psw' and len(cbk_data) == 5: # ok, psw, id, status, state
                            resp_type = 'evt'
                            self._psw_callback(cbk_data)

                    # LED response (not event) line received callback
                    if self._led_callback != None:
                        if cbk_data[1] == b'led' and len(cbk_data) == 5: # ok, led, id, fn, status
                            self._led_callback(cbk_data)

                # Got the Cmdex formatted response line, ready for a new request
                if resp_type == 'res':

                    # Clear waiting flag
                    self._cmdex_waiting = False
                    self._waiting_counter = 0
                    self._retry_counter = 0

                    # Perform callback if required
                    if self._last_cmd_cbk['cbk'] != None:

                        # Performs the callback
                        self._last_cmd_cbk['cbk'](cbk_data)
                        # self._cmdex_waiting = False

        except Exception as e:
            print(f'CmdexCore: Exception -> {e}')


    def put_comd_queue(self, command, callback):
        """ Puts a pair of command-callback into queue """
        cmd_cbk = {'cmd':command, 'cbk':callback}
        self._queue_cmd_cbk.append(cmd_cbk)


    def clr_interval(self, id):
        if id in self.__interval_objects:
            params = self.__interval_objects[id]
            params[3] = False # 3: enabled flag
            self.__interval_objects[id] = params


    def clr_timeout(self, id):
        clr_interval(id)


    def __create_interval_timeout(self, callback, interval, mode):

        if callable(callback):
            # 0: callback
            # 1: interval
            # 2: ticks
            # 3: enabled
            # 4: id
            # 5: counter
            # 6: mode, 0: continuous, 1: oneshot

            id = uuid.uuid1().hex[4:20]
            if interval < 10:
                interval = 10 # allowed minimum time is 10 mS

            self.__interval_objects[id] = [callback, interval, 0, True, id, 0, mode]
            if self._interval_thread == None:
                self.__start_interval()
        return id


    def set_interval(self, callback, interval):
        return self.__create_interval_timeout(callback, interval, 0)


    def set_timeout(self, callback, interval):
        return self.__create_interval_timeout(callback, interval, 1)


    def __proc_interval(self):
        tick_ms = 10e-3
        while self._thread_running == True:

            rm_list = []
            time.sleep(tick_ms)
            for key in self.__interval_objects:
                obj = self.__interval_objects[key]
                if obj[3] != True:
                    rm_list.append(obj)
                    continue

                # Timing
                obj[2] += tick_ms
                if obj[2] >= obj[1]/1000:
                    obj[2] = 0  # ticks
                    obj[5] += 1 # counter

                    # Callback
                    obj[0]( {'id':obj[4], 'counter':obj[5]} ) # id, counter, object

                    # Stop if it operates in one-short
                    if obj[6] == 1:
                        obj[3] = False

            for rm in rm_list:
                self.__interval_objects.pop(rm[4])
            rm_list.clear()


    def __start_interval(self):
        self._interval_thread = threading.Thread(None, self.__proc_interval, 'interval', daemon=False)
        self._interval_thread.start()


    @staticmethod
    def goto_github():
        url = 'https://github.com/drsanti/PyCmdex'
        print(f'Opening the {url}')
        webbrowser.open(url, new=1)


    @staticmethod
    def open_mcu_port(port):
        uart = serial.Serial(port=port, baudrate=115200,timeout=0.1)
        uart.rts = None
        uart.dtr = None
        time.sleep(2)
        uart.flushInput()
        uart.flushOutput()
        uart.read()
        return uart;

    @staticmethod
    def detect_mcu():

        ports = list_ports.comports()
        if len(ports) > 0:
            print('\nPort List:')
            print("\n".join([
                '   - ' + port.device + ': ' + port.description
                for port in ports
            ]))



        print('\nDetecting MCU board...')
        retry_flag  = True
        mcu_port    = None

        for port in ports:
            if retry_flag == False:
                break


            port_name = port.device;
            try:
                uart = serial.Serial(port=port_name, baudrate=115200,timeout=0.25)
                uart.rts = None
                uart.dtr = None
                time.sleep(2)
                uart.flushInput()
                uart.flushOutput()
                uart.read()

                if uart.isOpen():
                    uart.write(b'ver,0\r\n')
                    retry_count = 0

                    while retry_flag == True:
                        line = uart.readline()
                        if len(line) > 0:
                            # print(line)
                            sp = line.split(b',')
                            if sp[0] == b'ok: ver':
                                print(f'\nMCU-Port: {port_name}')
                                ver = ""
                                ver = ver.join(map(chr, sp[-1]))
                                print(f'MCUFirmware: {str(ver)}')
                                loop_flag = False
                                mcu_port = port_name
                                retry_count = 999
                                retry_flag  = False

                                break # Breaks while
                        else:
                            if mcu_port == None:
                                print(f'CmdexCore: Performs handshaking [{retry_count}/10]')
                                uart.read()
                                uart.write(b'ver,0\r\n')
                                retry_count += 1
                                if retry_count > 10:
                                    print(f'CmdexCore: MCU is not found @ {port_name}')
                                    break



            except Exception as e:
                print(e)


        # print(f'MCU@{mcu_port}')
        return mcu_port;
