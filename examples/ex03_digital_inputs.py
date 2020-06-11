# Import the Cmdex from
from PyCmdex.cmdex import Cmdex


# Create an Cmdex object.
cmdex = Cmdex()


#
# Example 1: Read status of push button switch
#

# Press/Release the PSW0 on the microcontroller board and check the result.
def check_psw_data(data):
    psw_data = cmdex.psw0; # can be the psw0, psw1, psw2, psw3
    print("PSW0: " + ("ON" if psw_data == True else "OFF"))

cmdex.set_interval( check_psw_data, 1000 )


#
# Example 2: Read status of PSW3 and write to LED3
#

# Press/Release the PSW3 on the microcontroller board and check the status of LED3.
def update_status(data0):
    cmdex.led3 = cmdex.psw3
    print("  LED3: " + ("ON" if cmdex.led3 == True else "OFF"))

cmdex.set_interval( update_status, 500 )
