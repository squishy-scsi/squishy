[<img src="https://raw.githubusercontent.com/squishy-scsi/squishy/main/contrib/img/sachi/electrichearts_20220323A_sachi_trans.png" align="right" width="400"/>](https://docs.scsi.moe/mascot.html)
# Squishy: The SCSI Multitool

Squishy is a platform for working with old SCSI devices with modern systems in a flexible manner. It was originally developed as a one-off solution for the [taperipper] project, which was to boot a modern system off of a IBM 9348-002 9-track magnetic tape drive.

It has since evolved into being a generic toolkit and hardware platform for all things SCSI.

Squishy is comprised of 4 core components; A gateware library built on [Torii]; A python library with various utilities and structures for dealing with SCSI data; A applet system to allow for custom gateware/python code applets to run on the hardware; And finally, the hardware itself.

> [!IMPORTANT]
> If you're looking for the Squishy hardware, the design files have moved to [`squishy-scsi/hardware`].

## Documentation

The documentation for Squishy can be found at [https://docs.scsi.moe].

## Installation

The installation instructions for squishy on various platforms can be found on the [Installation Instructions] page of the documentation.

## Hardware

The Squishy hardware design files have be migrated to [`squishy-scsi/hardware`].

Details about the squishy hardware can be found in the [Hardware] section of the online documentation.

## Mascot - Sachi

<img src="https://raw.githubusercontent.com/squishy-scsi/squishy/main/contrib/img/sachi/electrichearts_20211013A_sachi_trans_1024.png" align="left" width="350" alt="Sachi the spirit fox"/>

More information about Sachi is available on her [mascot page] in the documentation.

Sachi was designed and illustrated by the amazing [Tyson Tan (tysontan.com)]. He provides mascot design service for free and open source software projects, free of charge, under free license.

## Community

Squishy has a dedicated IRC channel, [#squishy on libera.chat]. Join to ask questions, discuss ongoing development, or just hang out.

**NOTE:** Squishy does not have an official discord, nor any endorsed discord servers, for an explanation as to why, see the [F.A.Q.]

## Licenses

The Squishy project is licensed under 3 individual licenses, one for the hardware, one for the gateware and software, and one for the documentation.

The hardware is licensed under the [CERN-OHL-S], the full text of which can be found in the [`squishy-scsi/hardware/LICENSE`] file.

The software and gateware are licensed under the [BSD-3-Clause], the full text of which can be found in the [`LICENSE`] file.

The documentation is licensed under the Creative Commons [CC-BY-SA 4.0], the full text of which can be found in the [`LICENSE.docs`] file.

Sachi, the mascot is dual-licensed under the [BSD-3-Clause] and the Creative Commons [CC-BY-SA].

[taperipper]: https://lethalbit.net/projects/taperipper/
[Torii]: https://github.com/shrine-maiden-heavy-industries/torii-hdl
[https://docs.scsi.moe]: https://docs.scsi.moe
[Installation Instructions]: https://docs.scsi.moe/install.html
[`squishy-scsi/hardware`]: https://github.com/squishy-scsi/hardware
[Hardware]: https://docs.scsi.moe/hardware/index.html
[mascot page]: https://docs.scsi.moe/mascot.html
[Tyson Tan (tysontan.com)]: https://tysontan.com
[#squishy on libera.chat]: https://web.libera.chat/#squishy
[F.A.Q.]: https://docs.scsi.moe/faq.html
[CERN-OHL-S]: https://ohwr.org/cern_ohl_s_v2.txt
[`squishy-scsi/hardware/LICENSE`]: https://github.com/squishy-scsi/hardware/tree/main/LICENSE
[BSD-3-Clause]: https://spdx.org/licenses/BSD-3-Clause.html
[`LICENSE`]: https://github.com/squishy-scsi/squishy/tree/main/LICENSE
[CC-BY-SA 4.0]: https://creativecommons.org/licenses/by-sa/4.0/
[`LICENSE.docs`]: https://github.com/squishy-scsi/squishy/tree/main/LICENSE.docs
