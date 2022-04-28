```{toctree}
:hidden:

introduction
install
getting_started
hardware/index
applets/index
library/index
tutorials/index
cli
gui
mascot
```
# Squishy: The SCSI Multitool

```{eval-rst}
.. figure:: ../../etc/img/sachi/electrichearts_20220323A_sachi_trans.png
	:align: right
	:figwidth: 350px
```

This is the documentation for Squishy and it's supporting components, as well as a collection of guides and tutorials for the Squishy ecosystem.


## What Squishy Isn't

It's important to detail what Squishy isn't, as it differs a lot from other devices intended to interact with older SCSI systems.

Squishy is not *only* a disk emulator like the [BlueSCSI](https://scsi.blue/) or the [SCSI2SD](https://www.codesrc.com/mediawiki/index.php?title=SCSI2SD). It is also not *only* a SCSI to USB Mass storage adapter.

Squishy is not a *specialized* device targeting only a single aspect of the SCSI ecosystem, nor targeting only a single platform.

## What Squishy Is

Squishy is a platform, it allows you to accomplish almost any goal you wish to that involves a SCSI bus. It can do things as mundane as emulating a SCSI hard drive, but also you can use it to [sniff, analyze, and reply SCSI bus traffic](./applets/analyzer.md), or even [boot a modern system from 9-track tape](./applets/taperipper.md).

It is comprised of a [gateware](./library/gateware/index.md) and [python](./library/python/index.md) library as well as a [hardware](./hardware/index.md) platform that acts as a bridge between the software and SCSI bus. Squishy allows for powerful and flexible control over all things SCSI, and using its [powerful applet system](./applets/index.md) it gives that power to you.


For a more detailed introduction to Squishy and it's components, see the [Introduction](./introduction.md) section of the documentation. Then, when you're ready visit the [Getting Started](./getting_started.md) section to get up an running.

Squishy is entirely open source, and under permissive licenses. The full source code, gateware, firmware, and hardware designs are available on [GitHub](https://github.com/lethalbit/squishy).

## Comparison

|                       | [Squishy](https://scsi.moe) | [BlueSCSI](https://scsi.blue/) | [SCSI2SD](https://www.codesrc.com/mediawiki/index.php/SCSI2SD) | [RaSCSI](https://github.com/akuker/RASCSI) |
|-----------------------|---------|----------|---------|--------|
| Has a cute mascot     | Yes     | No       | No      | No     |
| Device Emulation      | Yes     | Yes      | Yes     | Yes    |
| Non-Storage Emulation | Yes     | No       | No      | Yes<sup>1</sup> |
| Initiator Emulation   | Yes     | No       | No      | Yes<sup>1</sup> |
| Passive Bus Tapping   | Yes     | No       | No      | Yes    |
| Fully Open Source     | Yes     | No<sup>2</sup>       | No      | No<sup>2</sup>     |
| Standalone            | No<sup>3</sup> | Yes | Yes | Yes |
| Cost                  | ?       | ~50USD   | ~98USD  | ~45USD<sup>4</sup> |

**1:** RaSCSI allows you to write Linux userspace software via an API.

**2:** The adapter board is Open Source, but the main compute element is not.

**3:** Squishy requires USB power for operation, therefore it is considered to always be tethered.

**4:** This includes only the RaSCSI interface itself, and not the needed RaspberryPi SOM as well.
