```{warning}
Squishy hardware is specially designed and **is not** able to be substituted for other hardware at the moment. This include any popular development or eval boards.
```

# Hardware

```{toctree}
:hidden:

rev1
rev2
```

The squishy hardware is broken up into revisions and release levels. Each revision has breaking changes when it comes to hardware, and so they are their own platforms, however, release levels within each revision are hardware compatible with each other.

Both the revision and the release level start at 0, and increment by one. If the release level is omitted, it is assumed to be 0.

The format follows the `rev<#>[.#]` format, where `rev<#>` is the hardware revision and `[.#]` is the release level. so the following string, `rev8.3` is hardware revision 8, release 3.

Currently there are two hardware releases [`rev1`](./rev1.md) and [`rev2`](./rev2.md), see each page for details on each respective hardware revision.



## Getting Squishy Hardware

There are two main ways to get squishy hardware, buying it, or building it.

### Buying Hardware

```{note}
As of 2022-04-24, Squishy hardware is not available for sale, however, once engineering and validation of Revision 2 is completed, rev2 units are expected to be available to purchase.
```

### Building Hardware

Every released version of the Squishy hardware is archived and has full schematics, gerbers, Bill of Materials, and KiCad project files available.

The smallest parts are 0402 and all revisions contain at least one large BGA part. Assembly via a Pick-and-Place machine has not been tested, but should be possible as DFM was a large part of the process.
