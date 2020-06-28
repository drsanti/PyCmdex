"""
#************************************************************
#* File:    CmdexMcu.py                                     *
#* Author:  Asst.Prof.Dr.Santi Nuratch                      *
#*          Embedded Computing and Control Laboratory       *
#*          ECC-Lab, INC, KMUTT, Thailand                   *
#* Update:  23 May 2020                                     *
#************************************************************
"""

from PyCmdex.cmdex_apis import *
import time

class CmdexMcu(CmdexApis):

    PRINT_EVENTS = False

    def __init__(self, port=None, baudrate=115200, **kwargs):

        super().__init__(port, baudrate, **kwargs)

        #
        # Note:
        #   All properties will be updated when the cmdex-line is received
        #

        # LEDs

        self.__led0 = False

        self.__led1 = False
        self.__led2 = False
        self.__led3 = False

        # PSWs
        self.__psw0 = False
        self.__psw1 = False
        self.__psw2 = False
        self.__psw3 = False

        # ADCs
        self.__adc0 = -1
        self.__adc1 = -1
        self.__adc2 = -1
        self.__adc3 = -1

        # Add callbacks or register the events
        self.add_callback('led', lambda resp: self.__process_led_line(resp))
        self.add_callback('psw', lambda resp: self.__process_psw_line(resp))
        self.add_callback('adc', lambda resp: self.__process_adc_line(resp))

        self.__ready_callback = None
        if 'callback' in kwargs:
            self.__ready_callback = kwargs['callback']



        # Request all data, leds, psws, and adcs.
        self.get_all_data(self.__ready_callback, showInfo=True)




    def get_all_data(self, ready_callback=None, showInfo=False):
        """
        Aquires all channel of LEDs, PSW, and ADCs.
        The ready_callback function will be called when all data are received.
        All private variables representing to the LEDs, PSWs, and ADCs will be updated.
        """

        # Get LEDs
        for id in [0, 1, 2, 3]:
            self.led_get(id)

        # Get PSWs
        for id in [0, 1, 2, 3]:
            self.psw_get(id)

        # Get ADCs
        for id in [0, 1, 2, 3]:
            self.adc_get(id)

        # Waiting for all data, leds, psws, adcs.
        ticks = 0
        ready = True
        while True:
            ready = True
            time.sleep(1/100)
            ticks += 1
            if ticks > 200:
                print(
                    f'\r\nCmdexMcu: No response from the MCU.\r\n') if showInfo == True else None
                ready = False
                break
            for adc in self.get_adc_data():
                if adc < 0:
                    ready = False
            if ready == True:
                data = {'leds': self.get_led_data(), 'psw': self.get_adc_data(),
                        'adcs': self.get_adc_data()}
                print('\r\nCmdexMcu: Completed') if showInfo == True else None
                print(f"CmdexMcu: {data}\r\n") if showInfo == True else None
                break

        if ready == True and ready_callback != None:
            ready_callback({'leds': self.get_led_data(),'psw': self.get_psw_data(), 'adcs': self.get_adc_data()}, self)

        return self


    def get_led_data(self):
        """
        Returns the last update statuses of the LEDs, LED<3:0>.
        """
        return [self.__led3, self.__led2, self.__led1, self.__led0]


    def get_psw_data(self):
        """
        Returns the last update statuses of the PSWs, PSW<3:0>.
        """
        return [self.__psw3, self.__psw2, self.__psw1, self.__psw0]


    def get_adc_data(self):
        """
        Returns the last update values of the ADCs, ADC<3:0>.
        """
        return [self.__adc3, self.__adc2, self.__adc1, self.__adc0]


    # LED Event/Response
    def __process_led_line(self, resp):
        """
        Updats status of LED based on the cmdex-line received.
            - resp: bytes data sent from the MCU.
        """

        try:
            if self.is_cmdex_ok(resp):
                sp = self.split_cmdex_params(resp)
                id = int(sp[2])
                self.__update_led(id, resp)
                if id >= 0 and id <= 3 and CmdexMcu.PRINT_EVENTS == True:
                    print(f'led_event: {self.__led3},{self.__led2},{self.__led1},{self.__led0}')
        except Exception as e:
            print(f'CmdexMcu: Exception -> {e}')


    # PSW Event/Response
    def __process_psw_line(self, resp):
        """
        Updats status of PSW based on the cmdex-line received.
            - resp: bytes data sent from the MCU.
        """

        try:
            if self.is_cmdex_ok(resp):
                sp = self.split_cmdex_params(resp)
                id = int(sp[2])
                st = sp[3] == b'1'
                if id == 0:
                    self.__psw0 = st
                elif id == 1:
                    self.__psw1 = st
                elif id == 2:
                    self.__psw2 = st
                elif id == 3:
                    self.__psw3 = st

                if id >= 0 and id <= 3 and CmdexMcu.PRINT_EVENTS == True:
                    print(
                        f'psw_event: {self.__psw3},{self.__psw2},{self.__psw1},{self.__psw0}')
        except Exception as e:
            print(f'CmdexMcu: Exception -> {e}')


    # ADC Event/Response
    def __process_adc_line(self, resp):
        """
        Updats value of ADC based on the cmdex-line received
            - resp: bytes data sent from the MCU
        """

        try:
            if self.is_cmdex_ok(resp):
                sp = self.split_cmdex_params(resp)
                id = int(sp[2])
                val = int(sp[3])
                if id == 0:
                    self.__adc0 = val
                elif id == 1:
                    self.__adc1 = val
                elif id == 2:
                    self.__adc2 = val
                elif id == 3:
                    self.__adc3 = val

                if id >= 0 and id <= 3 and CmdexMcu.PRINT_EVENTS == True:
                    print(
                        f'adc_event: {self.__adc3},{self.__adc2},{self.__adc1},{self.__adc0}')
        except Exception as e:
            print(f'CmdexMcu: Exception -> {e}')


    # ADC0
    @property
    def adc0(self):
        return self.__adc0

    # ADC1
    @property
    def adc1(self):
        return self.__adc1

    # ADC2
    @property
    def adc2(self):
        return self.__adc2

    # ADC3
    @property
    def adc3(self):
        return self.__adc3

    # PSW0
    @property
    def psw0(self):
        return self.__psw0

    # PSW1
    @property
    def psw1(self):
        return self.__psw1

    # PSW2
    @property
    def psw2(self):
        return self.__psw2

    # PSW3
    @property
    def psw3(self):
        return self.__psw3

    # LED0
    @property
    def led0(self):
        return self.__led0

    @led0.setter
    def led0(self, status):
        id = 0
        self.led_wrt(id, status, lambda resp: self.__update_led(id, resp))

    # LED1
    @property
    def led1(self):
        return self.__led1

    @led1.setter
    def led1(self, status):
        id = 1
        self.led_wrt(id, status, lambda resp: self.__update_led(id, resp))

    # LED2
    @property
    def led2(self):
        return self.__led2

    @led2.setter
    def led2(self, status):
        id = 2
        self.led_wrt(id, status, lambda resp: self.__update_led(id, resp))

    # LED3
    @property
    def led3(self):
        return self.__led3

    @led3.setter
    def led3(self, status):
        id = 3
        self.led_wrt(id, status, lambda resp: self.__update_led(id, resp))



    # Called by the ledx.setter and the led-line-received-event
    def __update_led(self, id, resp):
        """
        Updats status of an LED

            - id:   LED's id (0,1,2,3)
            - resp: Response data (bytes data)
        """

        try:
            if type(resp) is bytes:
                resp = self.split_cmdex_params(resp)

            # Request:
            #        0      1       2     3     4
            # resp: [b'ok', b'led', b'0', b'1', b'1']

            # Event (MCU is restarted)
            #        0      1       2     3
            # resp: [b'ok', b'led', b'0', b'0']

            if resp[0] == b'ok':

                st = resp[-1] == b'1'

                if id == 0:
                    self.__led0 = st
                elif id == 1:
                    self.__led1 = st
                elif id == 2:
                    self.__led2 = st
                if id == 3:
                    self.__led3 = st
        except Exception as e:
            print(f'CmdexMcu: Exception -> {e}')
            pass
