# ************************************************************
# File:     cmdex_apis.py
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


#************************************************************
#* File:    CmdexApis.py                                    *
#* Author:  Asst.Prof.Dr.Santi Nuratch                      *
#*          Embedded Computing and Control Laboratory       *
#*          ECC-Lab, INC, KMUTT, Thailand                   *
#* Update:  22 May 2020                                     *
#************************************************************

from PyCmdex.cmdex_core import *


class CmdexApis(CmdexCore):

    def __init__(self, port=None, baudrate=115200, **kwargs):
        super().__init__(port, baudrate, **kwargs)

    def adc_get(self, id, callback=None):
        """
        Reads ad sends a 10-bit value (0-1023) of the ADC to the callback function.

        Parameters:

            - id: Channel ID of the ADC (0, 1, 2, 3).
            - callback:  Callback function called when got a response from MCU.
        """
        #                 id    value
        # [b'ok', b'adc', b'1', b'xxx']
        self.put_comd_queue('adc,{}\r\n'.format(id), callback)
        return self

    def adc_auto_detection(self, id, threshold, interval, callback=None):
        """ Sets analog inputs (AI0-AI3) auto-detection """
        self.put_comd_queue('det,{},{},{}\r\n'.format(id, threshold, interval), callback)
        return self

    def psw_get(self, id, callback=None):
        """ Sends status of the switch to the callback function """
        #                 id    status
        # [b'ok', b'psw', b'2', b'x']
        self.put_comd_queue('psw,{}\r\n'.format(id), callback)
        return self


    def led_set(self, id, callback=None):
        """ Sets status of the LED, and sends the current status (ON) to the callback function """
        #                  id   fn    status
        # [b'ok', b'led', b'2', b'1', b'1']
        self.put_comd_queue('led,{},1\r\n'.format(id), callback)
        return self

    def led_clr(self, id, callback=None):
        """ Resets status of the LED, and sends the current status (OFF) to the callback function """
        #                  id   fn    status
        # [b'ok', b'led', b'2', b'0', b'0']
        self.put_comd_queue('led,{},0\r\n'.format(id), callback)
        return self

    def led_inv(self, id, callback=None):
        """ Toggles/Inverts status of the LED, and sends the current status (OFF/ON) to the callback function """
        #                 id    fn    status
        # [b'ok', b'led', b'0', b'2', b'x']
        self.put_comd_queue('led,{},2\r\n'.format(id), callback)
        return self

    def led_wrt(self, id, status, callback=None):
        """ Writes status to the LED, and sends the current status (OFF/ON) to the callback function """
        #                 id    fn    status
        # [b'ok', b'led', b'0', b'2', b'x']
        fn = 0
        if status == 1 or status == True:
            fn = 1
        elif  status == 0 or status == False:
            fn = 0
        else:
            fn = 2
        self.put_comd_queue('led,{},{}\r\n'.format(id, fn), callback)
        return self

    def led_get(self, id, callback=None):
        """ Sends status (OFF/ON) of the LED to the callback function """
        #                 id    fn    status
        # [b'ok', b'led', b'2', b'3', b'x']
        self.put_comd_queue('led,{},3\r\n'.format(id), callback)
        return self

    def led_fls(self, id, interval, callback=None):
        """ Flash """
        self.put_comd_queue('fls,{},{}\r\n'.format(id, interval), callback)
        return self


    def led_blk(self, id, delay, interval, callback=None):
        """ Blink """
        self.put_comd_queue('blk,{},{},{}\r\n'.format(id, delay, interval), callback)
        return self


    def led_cps(self, id, delay, width, period, callback=None):
        """ Continuous Pulse Signal """
        self.put_comd_queue('cps,{},{},{},{}\r\n'.format(id, delay, width, period), callback)
        return self


    def flash(self, id, interval, callback=None):
        """ Flash """
        led_fls(id, interval, callback)
        return self


    def blink(self, id, delay, interval, callback=None):
        """Blink """
        led_blk(id, delay, interval, callback)
        return self


    def pulse(self, id, delay, width, period, callback=None):
        """ Continuous Pulse Signal """
        led_cps(id, delay, width, period, callback)
        return self


    def buzzer(self, interval, frequency=500, power=50, callback=None, **kwargs):
        """
        Generates beep sound.

            - interval: Beep interval (ms).
            - frequency: Beep frequency in Hertz.
            - power: Beep power (%)
            - callback: Callback function called when got a response from MCU.
        """
        if callback == None:
            callback = kwargs.pop('callback') if 'callback' in kwargs else None
        self.put_comd_queue('buz,{},{},{}\r\n'.format(interval, frequency, power), callback)
        return self

    def pwm(self, id, function, value, callback=None):
        """ PWM Controller (4-channel, 0.95Hz–160kHz, 0-100% duty ratio, 0-100% phase-shift) """
        # fn 0: frequency
        # fn 1: duty
        # fn 2: phase-shift
        # fn 3: stop/start
        self.put_comd_queue('pwm,{},{},{}\r\n'.format(id, function, value), callback)
        return self


    def get_clock(self, type, callback=None):
        """ Sends system clock/time of the MCU to the callback function """
        # type: 0 – HH:MM:SS:xxx    --> [b'ok', b'ckk', b'0', b'00:00:18.620']
        # type: 1 – Microseconds    --> [b'ok', b'time', b'1', b'397960736.000']
        # type: 2 - Milliseconds    --> [b'ok', b'time', b'2', b'411280.781']
        self.put_comd_queue('clk,{}\r\n'.format(type), callback)
        return self


    def get_cmdex_version(self, type=1, callback=None):
        """ Returns version information """
        if type == 0 or type == '0':
            self.put_comd_queue('ver,{}\r\n'.format(type), callback)
        else:
            version =  'cmdex.core.1.0.1 (MCU Firmware)\r\n'
            version += 'Asst.Prof.Dr.Santi Nuratch\r\n'
            version += 'Embedded Computing and Control Laboratory\r\n'
            version += 'ECC-Lab, INC-KMUTT, Thailand\t\n'
            version += '27 May 2020\r\n'
            if callback != None:
                callback(version)
            else:
                print(f'\r\n{version}\r\n')
        return self
