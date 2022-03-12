# Keithley DMM

A library of scripts that implement basic functionality to read and controll old Keithley DMMs over GPIB bus. Scripts make use of [PyVISA](https://pyvisa.readthedocs.io/en/latest/index.html) package for GPIB communication.

Currently only two models are supported:

* Keithley 196
* Keithley 199

## Usage

Scripts in the KeithleyDMM directory can be used as standalone CLI aplications (run scripts with `-h` option to get help on running standalone):

```
$ ./keithley196.py -a 7 -s
Using primary address 7 on GPIB port 0

 --- Instrument status ---

Function ... V DC
Range ...... 30 VDC
Zero ....... DISABLED
Filter ..... 0

 --- Instrument status ---

-0.00038 V DC
```

or as a part of other python programs by importing the KeithleyDMM library (make sure that python interpreter can find it):

```
import KeithleyDMM

k196 = KeithleyDMM.keithley196(pad=7)
k199 = KeithleyDMM.keithley199(pad=1)

m1 = k196.raed()
m2 = k199.raed()
...
```

## Examples

### example_dual_logger.py

Opens two instruments and periodicaly writes timestamps, measured values and asociated uints to a .csv file

### example_scroll.py

Scrolls trough long a message string on the instrument display

## Compatibility

Scripts are using PyVISA as an abstraction layer for GPIB communication, so they should be compatible with different operating system and GPIB interface hardware combinations as long as the said combinations are supported by PyVISA.
