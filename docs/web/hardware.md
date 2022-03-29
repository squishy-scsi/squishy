# Hardware

The squishy hardware is broken up into revisions and release levels. Each revision has breaking changes when it comes to hardware, and so they are their own platforms, however, release levels within each revision are hardware compatible with each other.

Both the revision and the release level start at 0, and increment by one. If the release level is omitted, it is assumed to be 0.

The format follows the `rev<#>[.#]` format, where `rev<#>` is the hardware revision and `[.#]` is the release level. so the following string, `rev8.3` is hardware revision 8, release 3.


## Revision 0

Hardware revision 0 was a preliminary engineering effort and has not seen a release.

### Capabilities

Due to a design flaw in the SCSI front-end, rev0 was entirely unusable.

## Revision 1

Hardware revision 1 was the first release of the Squishy hardware, it is only capable of speaking SCSI HVD. Revision 1 release 0 has some problems that can be fixed with two component replacements, which was not enough to constitute a whole new release.

### Capabilities

Revision 1 is still in the validation phase, as such is capabilities have not been fully cataloged.

## Revision 2

Hardware revision 2 is an overhaul in an attempt to increase the abilities of Squishy, it replaces the iCE40 FPGA with the ECP5-5G allowing for USB-3.

It also has a entirely re-designed front-end allowing for it to speak all possible variations of SCSI.

### Capabilities

Revision 2 is still in the engineering phase, as such is capabilities have not been fully cataloged.

## Getting Squishy Hardware

There are two main ways to get squishy hardware, buying it, or building it.

### Buying Hardware

Currently, as of 2022-03-29, Squishy hardware is not available for sale, however, once engineering and validation of Revision 2 is completed, rev2 units are expected to be available to purchase. 

### Building Hardware

Every released version of the Squishy hardware is archived and has full schematics, gerbers, Bill of Materials, and KiCad project files available.

The smallest parts are 0402 and all revisions contain at least one large BGA part. Assembly via a Pick-and-Place machine has not been tested, but should be possible as DFM was a large part of the process.
