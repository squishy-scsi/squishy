# Squishy

Squishy is a toolkit for working with old SCSI devices with modern systems in a flexible manner.

It was originally developed as a one-off solution for the [taperipper](https://lethalbit.net/projects/taperipper/) project, which was to boot a modern system off of a IBM 9348-002 9-track magnetic tape drive. It has since evolved into being a generic toolkit and hardware platform for SCSI.

## Software

Squishy includes an [Amaranth HDL](https://github.com/amaranth-lang/amaranth) gateware library to allow one to add SCSI functionality to any project.

In addition to the gateware library, it also includes a set of utilities for interacting with SCSI devices, hosts, and existing bus'. It has a traffic analyzer, traffic generator, protocol dissector, and other utilities to allow for an out-of-the box experience.

Along with this, it has a powerful applet infrastructure that leverages the hardware and existing gateware library to develop custom applets that allow you to interact with SCSI at any layer.

## Hardware

The squishy hardware is your gateway into the world of old SCSI devices via a modern system. It implements the bus interface used to interact with the SCSI bus and hosts the gateware responsible for the extensible platform on which applets can be built to run as close to the SCSI layer as you want without building hardware yourself.

## Documentation

The documentation for Squishy can be found at [https://lethalbit.github.io/squishy](https://lethalbit.github.io/squishy).

## Installation

The installation instructions for squishy on various platforms can be found on the [https://lethalbit.github.io/squishy/install](https://lethalbit.github.io/squishy/install) page. 

Alternatively, follow one of the following links for your platform:

 * [Linux Install Instructions](https://lethalbit.github.io/squishy/install/index.html#linux)
 * [macOS Install Instructions](https://lethalbit.github.io/squishy/install/index.html#macos)
 * [Windows Install Instructions](https://lethalbit.github.io/squishy/install/index.html#windows)

## Mascot - Sachi

![Sachi the spirit fox](https://raw.githubusercontent.com/lethalbit/squishy/main/etc/img/sachi/electrichearts_20211013A_sachi_trans_1024.png)

More information about Sachi is available on her [mascot page](https://lethalbit.github.io/squishy/mascot.html) in the documentation.

Sachi was designed and illustrated by the amazing [Tyson Tan (tysontan.com)](https://tysontan.com). He provides mascot design service for free and open source software projects, free of charge, under free license.

## Licenses

The Squishy project is licensed under 3 individual licenses, one for the hardware and gateware, one for the software and one for the documentation.

The hardware is licensed under the [CERN-OHL-S](https://ohwr.org/cern_ohl_s_v2.txt), the license for which can be found in [LICENSE.hardware](https://github.com/lethalbit/squishy/tree/main/LICENSE.hardware)

The software and gateware are licensed under the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) and can be found in [LICENSE.software](https://github.com/lethalbit/squishy/tree/main/LICENSE.software).

The documentation is licensed under the Creative Commons [CC-BY-SA](https://creativecommons.org/licenses/by-sa/2.0/) and can be found in [LICENSE.docs](https://github.com/lethalbit/squishy/tree/main/LICENSE.docs)

The icons used in the GUI are from the [KDE](https://kde.org) project. They are the [breeze-icons](https://github.com/KDE/breeze-icons/) and they are licensed under the [LGPL v2.1](https://spdx.org/licenses/LGPL-2.1-only.html), and can be found in [LICENSE.icons](https://github.com/lethalbit/squishy/tree/main/LICENSE.icons) 

The fonts used in the GUI are [Fira Code](https://github.com/tonsky/FiraCode), and [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans), both of which are under the [OFL 1.1](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL), and can be found in [LICENSE.fonts](https://github.com/lethalbit/squishy/tree/main/LICENSE.fonts)

The print/pdf documentation uses the font [Nunito](https://fonts.google.com/specimen/Nunito) which is under the [OFL 1.1](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL), and can be found in [LICENSE.fonts](https://github.com/lethalbit/squishy/tree/main/LICENSE.fonts)

Sachi, the mascot is dual-licensed under the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) and the Creative Commons [CC-BY-SA](https://creativecommons.org/licenses/by-sa/2.0/)
