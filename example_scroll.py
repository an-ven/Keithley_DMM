#!/bin/python3
import time
import KeithleyDMM

msg_string = "--- INITIATE THE RELEASE OF MAGIC SMOKE ---"

inst = KeithleyDMM.keithley196(pad=7, port=0)

try:
    print('Hit ctrl-c to abort.')

    # Put one display length padding before and after message string
    msg_string = (' '*10 + msg_string + ' '*10)
    # Loop untill interrupted
    while 1:
        # Scroll trough the message
        for i in range(len(msg_string)-10):
            # Send partial string to instrument
            inst.print(msg_string[i:i+10])
            time.sleep(0.1)
except KeyboardInterrupt:
    # Clean up
    inst.print('')
