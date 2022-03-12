#!/bin/python3
import time
import sys

# Import Keithley DMM library
import KeithleyDMM

# Instrument connection settings
gpib_port = 0
k196_addr = 7
k199_addr = 1

try:

    # Instantiate instruments
    k196 = KeithleyDMM.keithley196(k196_addr)
    k199 = KeithleyDMM.keithley199(k199_addr)

    # Open new .csv log file with start time in its name
    f = open(time.strftime('Log_%Y-%m-%d_%H-%M-%S.csv'), 'a')

    # Loop untill stoprd by ctrl-c
    while(1):
        # Get Current Time
        timestamp = time.localtime()
        # Read instruments
        v1 = k196.read()
        v2 = k199.read()
        # Get measurement units
        u1 = k196.units
        u2 = k199.units
        # Make date and time strings
        d = time.strftime('%Y-%m-%d', timestamp)
        t = time.strftime('%H:%M:%S', timestamp)
        # Assemble output string
        out_str =  (d + '; ' + t + '; ' + str(v1) + '; ' + u1 + '; ' + str(v2) + '; ' + u2)
        # Write output string to file
        f.write(out_str + '\n')
        print(out_str)
        # Wait for a bit before repeating
        time.sleep(1)

except KeyboardInterrupt:
    # Close file and exit
    f.close()
    sys.exit(0)

