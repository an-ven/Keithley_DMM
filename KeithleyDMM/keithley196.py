#!/bin/python3
import time

class keithley196:

    # Some constant translation lists
    FUNCTION_LIST = ['VDC', 'VAC', 'OHM', 'ADC', 'AAC', 'VDB', 'ADB', 'OCO']
    FUCTION_NAMES = ['Voltage DC', 'Voltage AC', 'Resistance', 'Current DC', 'Current AC', 'Voltage dB', 'Current dB', 'Offset Compensated Resistance']
    FUNCTION_UNITS = ['V DC', 'V AC', 'Ohm', 'A DC', 'A AC', 'dB V', 'dB A', 'Ohm (offset comp']
    RANGE_TABLE = [
        ['auto VDC', '300 mVDC', '3 VDC', '30 VDC', '300 VDC', '300 VDC', '300 VDC', '300 VDC'],
        ['auto VAC', '300 mVAC', '3 VAC', '30 VAC', '300 VAC', '300 VAC', '300 VAC', '300 VAC'],
        ['auto Ohm', '300 Ohm', '3 kOhm', '30 kOhm', '300 kOhm', '3 MOhm', '30 MOhm', '300 MOhm'],
        ['auto ADC', '300 uADC', '3 mADC', '30 mADC', '300 mADC', '3 ADC', '3 ADC', '3 ADC'],
        ['auto AAC', '300 uAAC', '3 mAAC', '30 mAAC', '300 mAAC', '3 AAC', '3 AAC', '3 AAC'],
        ['auto dBV', 'auto dBV', 'auto dBV', 'auto dBV', 'auto dBV', 'auto dBV', 'auto dBV', 'auto dBV'],
        ['auto dBA', 'auto dBA', 'auto dBA', 'auto dBA', 'auto dBA', 'auto dBA', 'auto dBA', 'auto dBA'],
        ['auto Ohm', '300 Ohm', '3 kOhm', '30 kOhm', '30 kOhm', '30 kOhm', '30 kOhm', '30 kOhm'],
    ]
    ZERO_MODES = ['DISABLED', 'ENABLED', 'USING ZERO VALUE']
    INSW_STATES = ['FRONT', 'REAR']

    # ==========================================================================
    # Class constructor: initialize GPIB to address the instrument, set output format and read status word
    # ==========================================================================
    def __init__(self, pad = 7, port = 0):
        # Import pyvisa
        import pyvisa
        # Instantiate instrument with specified primary adderess and GPIB port 
        pyvisa_rm = pyvisa.ResourceManager()
        resource_name = 'GPIB' + str(port) + '::' + str(pad)
        self.inst = pyvisa_rm.open_resource(resource_name)
        # Configure the instrument to output data with prefix
        self.inst.write('G0X')
        # Read instrument status word
        self.read_status()


    # ==========================================================================
    # Read datd fom instrument, determin unit ofmeasurement and return measurement value as float
    # ==========================================================================
    def read(self):
        # Read data from instrument, strip whitespace characters and separate data in to a list of fields separated by commas
        ans = self.inst.read().strip().split(',')
        # Save query timestamp
        self.timestamp = time.localtime()

        # Get the reading field
        r = ans[0]    
        # separate prefix and convert measurement value
        pfx = r[1:4]
        val = float(r[4:])
        # Use prefix to update units
        if (pfx == 'DCV'):
            self.units = 'V DC'
        elif (pfx == 'ACV'):
            self.units = 'V AC'
        elif (pfx == 'OHM') or (pfx == 'OCO') :
            self.units = 'Ohm'
        elif (pfx == 'DCI'):
            self.units = 'A DC'
        elif (pfx == 'ACI'):
            self.units = 'A AC'
        elif (pfx == 'dBV'):
            self.units = 'dB V'
        elif (pfx == 'dBI'):
            self.units = 'dB A'

        # return measurement value
        return val


    # ==========================================================================
    # Read instrument status word
    # ==========================================================================
    def read_status(self):

        # Send "U0X" command to request instrument status word and read result
        st = self.inst.query('U0X').strip()

        # Sanity check the status word length and model number prefix
        if st[0:3] != '196':
            raise ValueError("Unexpected status word model prefix")
        if len(st) != 31:
            raise ValueError("Unexpected status word length")
        
        # Split status word and save individual values
        self.status_autocal_mux = int(st[3])
        self.status_reading_mode = int(st[4])
        self.status_function = int(st[5])
        self.status_data_format = int(st[6])
        self.status_selftest = int(st[7])
        self.status_eoi_bus_holdoff = int(st[8])
        self.status_srq = int(st[9:11])
        self.status_exp_filter = int(st[11])
        self.status_filter = int(st[12:14])
        self.status_data_store_rate = int(st[14:20])
        self.status_range = int(st[20])
        self.status_rate = int(st[21])
        self.status_trigger = int(st[22])
        self.status_delay = int(st[23:28])
        self.status_terminator = int(st[28])
        self.status_zero = int(st[29])
        self.status_cal_sw = int(st[30])

        # Return Status word
        return st
    

    # ==========================================================================
    # Read instrument error word
    # ==========================================================================
    def read_error(self):
        er = self.instr.query("U1X")
        return er


    # ==========================================================================
    # Set measurement range
    # ==========================================================================
    def range(self, rng):
        # Check if input parameter is of valid type (integer)
        if isinstance(rng, int):
            # Check if input parameter value is in valid range
            if rng>=0 and rng<=7:
                # Send range command to instrument and return requested range value
                self.inst.write('R'+str(rng)+'X')
                return rng
            else:
                # else raise ValueError exception
                raise ValueError("Only values from 0 to 7 represent valid measurement ranges")
        else:
            # else raise TypeError exception
            raise TypeError


    # ==========================================================================
    # Set measurement function
    # ==========================================================================
    def function(self, fn):
        # check input parameter type
        if isinstance(fn, int):
            if fn>=0 and fn<=7:
                self.inst.write("F"+str(fn)+"X")
                return fn
            else:
                # else raise ValueError exception
                raise ValueError("Only integer values from 0 to 7 represent valid functions")
        elif isinstance(fn, str):
            # Convert input string to upper case, remove whitespace characters including spaces in the midle of the string
            fs = fn.upper().strip().replace(' ', '')
            # Try to find a matching function to select
            if fs=='VDC' or fs=='DCV':
                self.inst.write("F0X")
            elif fs=='VAC' or fs=='ACV':
                self.inst.write("F1X")
            elif fs=='OHM' or fs=='OHMS':
                self.inst.write("F2X")
            elif fs=='ADC' or fs=='DCA':
                self.inst.write("F3X")
            elif fs=='AAC' or fs=='ACA':
                self.inst.write("F4X")
            elif fs=="VDB":
                self.inst.write("F5X")
            elif fs=="ADB":
                self.inst.write("F6X")
            elif fs=='OCO':
                self.inst.write("F7X")
            else:
                raise ValueError("Unknown function string: " + str(fn))
        else:
            # else raise TypeError exception
            raise TypeError


    # ==========================================================================
    # Set zero
    # ==========================================================================
    def zero(self, mode=0, val=0):
        if mode==0:
            # Turn off zero mode
            self.inst.write('Z0X')
        elif mode==1:
            # Turn on zero mode
            self.inst.write('Z1X')
        elif mode==2:
            if val!=0:
                s = str(float(val))
                self.inst.write('V'+s+'XZ2X')
            else:
                self.inst.write('Z1X')
        else:
            raise ValueError("Invalid zero mode value")
    

    # ==========================================================================
    # Set Digital Filter
    # ==========================================================================
    def filter(self, n):
        if isinstance(n, int):
            if n>=0 and n<=99:
                self.inst.write('P'+str(n)+'X')
            else:
                raise ValueError("Filter parameter out of range (0 <= N <= 99")
        else:
            raise TypeError("Invalid input type. Filter parameter must be int")


    # ==========================================================================
    # Print message to display
    # ==========================================================================
    def print(self, t):
        # Check input type
        if isinstance(t, str):
            # Check length
            if len(t)<=10:
                # Replace spaces with @ characters to properly display on instruments
                t = t.replace(" ", "@")
                # Convert to upper case for consistency
                t = t.upper()
                # Replace any upper case X (used as execute command) with lower case x (gets displayed instead of executed)
                t = t.replace('X', 'x')
                # Write comand and string to instrument
                self.inst.write("D"+t+"X")
            else:
                raise ValueError("String too long")
        else:
            raise TypeError("Valid input type: string")


# ==============================================================================
# When running as standalone program
# ==============================================================================
if __name__=="__main__":
    import sys
    import getopt

    # Print help function
    def print_usage():
        print('''
Keithley196.py standalone mode quick help

Summary:
    A simple scrip implementing some basic functionality for reading and controlling a Keithley 196 DMM over a GPIB bus
    If no additional options are passed, the script will just read and print current measurement value form the default address 7 on GPIB port 0

Usage:
    keithley196.py [-g PORT_NUM] [-a PAD] [-v VALUE] [-f FUNCTION|?] [-r RANGE|?] [-Z] [-z] [-P] [-p] [-D MSG] [-d] [-s] [-h]

Options:
    -g [GPIB bus number]    Specify GPIB port number (default is 0)
    -a [Primary address]    Specify GPIB primary address of the instrument (For K196 default is 7)
    -v [Some Value]         Specify a numeric value to use with some other function like zero offser or filter
    -f [function]           Select measurement function (use parameter '?' to list valid functions)
    -r [range]              Select measurement range (use parameter '?' to list valid ranges for selected measurement function)
    -Z                      Enable zero mode (use -v for custom zero value, the default value is current measurement value)
    -z                      Disable zero mode
    -P                      Enable digital filter (use -v to specify a custom filter value, the default value is 10)
    -p                      Disable digital filter
    -D [mesage]             Display a custom message (up to 10 characters) on the instrument display
    -d                      Clear custom message display
    -s                      Print instrument status
    -h                      Print this help message

Examples:
    keithley196.py -f OHM -r 3    # Set measurement function to resistance and range to 3kOhm (note that function gets set first and than range)
    keithley196.py -Z -v 3.14159  # Enable zero offset with custom value of 3.14159
    keithley196.py -r ?           # List valid measurement ranges for current measurement function
    keithley196.py -D KEITHLEY    # Print "KEITHLEY" on instrument display

        ''')

    # Print Instrument status function
    def print_status():
        # Update status
        k196.read_status()
        # Print which primary address is beiong adressed on which GPIB port
        print("Using primary address " + str(primary_addr) + " on GPIB port " + str(gpib_port) )
        print("\n --- Instrument status --- \n")
        print("Function ... " + k196.FUNCTION_UNITS[k196.status_function])
        print("Range ...... " + k196.RANGE_TABLE[k196.status_function][k196.status_range])
        print("Zero ....... " + k196.ZERO_MODES[k196.status_zero])
        print("Filter ..... " + str(k196.status_filter))
        print("\n --- Instrument status --- \n")
    
    # Print valid measurement functions
    def print_functions():
        print('Valid measurement functions:')
        for f in range(len(k196.FUNCTION_LIST)):
            print('\'' + k196.FUNCTION_LIST[f] + '\' = ' + k196.FUCTION_NAMES[f])
        print(' ')

    # Print valid ranges for current measurement function
    def print_ranges():
        # Update status
        k196.read_status()
        print('Valid measurement ranges:')
        ranges = []
        for i, r in enumerate(k196.RANGE_TABLE[k196.status_function]):
            if not r in ranges:
                ranges.append(r)
                print('\'' + str(i) + '\' = ' + r)
        print(' ')

    # Get comandline arguments
    argv = sys.argv[1:]
    # Try to parse arguments
    try:
        opts, args = getopt.getopt(argv, 'g:a:hv:sr:f:zZpPdD:')
    except getopt.GetoptError as err:
        print(err)
        print_usage()
        sys.exit()

    # Default GPIB port number and instrument prmary address
    gpib_port = 0
    primary_addr = 7
    
    custom_val = 0

    # Parse arguments before initializing talking to the instrument
    for opt, arg in opts:
        if opt=='-g':       # Specify GPIB port number to use
            gpib_port = int(arg)
        elif opt=='-a':     # Specify instrument GPIB primary address
            primary_addr = int(arg)
        elif opt=='-h':     # Print help text
            print_usage()
            exit()
        elif opt=='-v':     # Set custom parameter value
            custom_val = float(arg)

    # Instantiate instrument object
    k196 = keithley196(primary_addr, gpib_port)
    
    # Parse arguments after connecting to the instrument
    for opt, arg in opts:
        if opt=='-s':       # Print instrument status
            print_status()
        elif opt=='-r':     # Set measurement range
            if arg == '?':
                print_ranges()
            else:
                k196.range(int(arg))
        elif opt=='-f':     # Set measurement function
            if arg == '?':
                print_functions()
            else:
                k196.function(arg)
        elif opt=='-z':     # Disable zero mode
            k196.zero(0)
        elif opt=='-Z':     # Enable zero mode
            # Check if a custom parameter value has been specified
            if custom_val != 0:
                k196.zero(2, custom_val)
            else:
                k196.zero(1)
        elif opt=='-p':     # Disable digital filter
            k196.filter(0)
        elif opt=='-P':
            # Check if a custom parameter value has been specified
            if custom_val != 0:
                k196.filter(int(custom_val))
            else:
                k196.filter(10)
        elif opt=='-D':   # Print a message on display
            k196.print(arg)
        elif opt=='-d':   # Clear message from display
            k196.print('')


    # Get reading valu and unit
    val = k196.read()
    unt = k196.units
    print(str(val) + " " + unt )
    