# Squishy

Squishy is a toolkit for working with old SCSI devices with modern systems in a flexible manner.

It was originally developed as a one-off solution for the [taperipper](https://lethalbit.net/projects/taperipper/) project, which was to boot a modern system off of a IBM 9348-002 9-track magnetic tape drive. It has since evolved into being a generic toolkit and hardware platform for SCSI.

## Software

Squishy is designed as both a set of utilities, and an extendable platform for dealing with SCSI. Along with the core Squishy gateware, it has things such as traffic generators and dissectors.

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

## Licenses

The Squishy project is licensed under 3 individual licenses, one for the hardware and gateware, one for the software and one for the documentation.

The hardware is licensed under the [CERN-OHL-S](https://ohwr.org/cern_ohl_s_v2.txt), the license for which can be found in [LICENSE.hardware](LICENSE.hardware)

The software and gateware are licensed under the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) and can be found in [LICENSE.software](LICENSE.software).

The documentation is licensed under the Creative Commons [CC-BY-SA](https://creativecommons.org/licenses/by-sa/2.0/) and can be found in [LICENSE.docs](LICENSE.docs)

The icons used in the GUI are from the [KDE](https://kde.org) project. They are the [breeze-icons](https://github.com/KDE/breeze-icons/) and they are licensed under the [LGPL v2.1](https://spdx.org/licenses/LGPL-2.1-only.html), and can be found in [LICENSE.icons](LICENSE.icons) 

The fonts used in the GUI are [Fira Code](https://github.com/tonsky/FiraCode), and [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans), both of which are under the [OFL 1.1](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL), and can be found in [LICENSE.fonts](LICENSE.fonts)
