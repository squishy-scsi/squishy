# Extra Utilities

Squishy has some extra utilities that are possibly useful.

## scsidump

`scsidump` is a [Wireshark] [extcap] interface to allow for direct packet-level capture of a SCSI bus with Squishy attached to it.

This is much like the [`analyzer`] applet, and, in fact, uses it behind the scenes, but only supports high-level packet-based captures of the SCSI bus, and not raw trace data from the bus.

### Installing

To install `scsidump`, simply copy or symlink the [`scsidump`] python file into `~/.local/lib/wireshark/extcap`, you might need to create the directory if it doesn't exist already.

Ensure that the `squishy` python package is in your python path as well, if you followed the
[installation instructions] it should already be there.

### Using

If installed and working properly, you will now see a new entry in the Wireshark capture list called 'Squishy SCSI Bus capture'.

Click the small gear icon next to the entry in the list to setup the capture configuration, it has most of the same options as the [`analyzer`] applet does.

When done, save the configuration and then double click the capture interface to start capturing with the attached Squishy.

[Wireshark]: https://www.wireshark.org/
[extcap]: https://www.wireshark.org/docs/man-pages/extcap.html
[`scsidump`]: https://github.com/squishy-scsi/squishy/blob/main/contrib/scsidump
[installation instructions]: ./install.md
[`analyzer`]: ./applets/analyzer.md
