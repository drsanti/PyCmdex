# Import the Cmdex
from PyCmdex.cmdex import Cmdex

# Create an object of the Cmdex
cmdex = Cmdex()


# The set_interval function requires 2 parameters
#   - function or lambda
#   - time (ms)

#
# Example 1: Using a lambda function
#

# Create an interval and give it a lambda function and time (500 mS)
cmdex.set_interval( lambda res: cmdex.led_inv(0), 500 );



#
# Example 2: Using a normal function
#

# This funtion will be executed evey 1000 mS
def toggle_led3(res):
    cmdex.led_inv(3)

# Create an interval and give it a function and time (1000 mS)
cmdex.set_interval( toggle_led3, 1000 );
