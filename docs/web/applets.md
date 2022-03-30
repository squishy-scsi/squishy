# Squishy Applets

## What is an Applet?

An applet is a portion of Amaranth HDL and supporting Python code that give functionality to the Squishy hardware.

## Built-in Applets

There are currently two built-in Applets, the analyzer, and taperipper.

### Analyzer

The analyzer applet turns squishy into a passive SCSI bus sniffer, allowing for you to inspect, copy, replay, and modify SCSI traffic.

### Taperipper

The taperipper applet turns squishy into a bootable interface for SCSI based 9-track tape drives, to allow for booting modern machines off of tape.


## Custom Applets

Squishy allows you to run your own custom applets, any python packages in the `SQUISHY_APPLETS` directory are attempted to be loaded as an applet, and then exposed to the user to allow them to invoke.

For more details, see the tutorial on custom applets.
