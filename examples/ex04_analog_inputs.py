# Import the Cmdex from
from PyCmdex.cmdex import Cmdex


# Create an Cmdex object.
cmdex = Cmdex()


# Move your hand over the microcontroller board and check the result in the console window.
# Note: the ADC1 is connected to the LDR
def read_adc_data(data):
    adc1_data = cmdex.adc1; # can be the adc0, adc1, adc2, adc3
    print("ADC1: " + str(adc1_data));

cmdex.set_interval( read_adc_data, 1000 )
