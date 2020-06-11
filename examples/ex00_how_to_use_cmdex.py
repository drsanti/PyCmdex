# Step 1) Import the Cmdex from
from PyCmdex.cmdex import Cmdex


# Step 2) Create an Cmdex object.
cmdex = Cmdex()


# Step 3) Add lines of code and save the script
cmdex.set_interval( lambda x: cmdex.led_inv(0), 500 );


# Step 4) Run the script using the command:
#         `python script_name.py`


# Step 5) Check the result in the console window and microcontroller board.

# Step 6) Stop or terminate the script by pressing the key `CTRL+ArrowUp`
