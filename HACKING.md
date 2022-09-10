# Information and Terminology Guide

This file is a resource in order to hopefully get someone who is unfamiliar with the codebase
or terminology up to speed enough to quickly be able to successfully understand and make changes
within the codebase.

The information here is likely incomplete, but there will be ongoing effort in order ensure it is
as up-to-date as possible.

## Repository Structure

This repository is broken up into several sections. The root of this repository contains files that are globally applicable, such as the licenses, readme, and various editor and linting configurations.

Within the root of this repository there are six sub directories:
 * [.github](./.github/) - Various metadata for github, such as workflow and issue templates
 * [contrib](./contrib/) - Non-executable data files, like fonts, images, and config files, as well as packaging scripts.
 * [docs](./docs/) - Sphinx documentation
 * [examples](./examples/) - Examples for using Squishy
 * [hardware](./hardware/) - The hardware files used to design and manufacture Squishy boards
 * [squishy](./squishy/) - The actual source for the Squishy package itself


Each directory has it's own layout in an attempt to be as logical as possible. However the hardware and squishy directories might need some possible further explantation.

### The [hardware](./hardware/) Directory

This directory contains two main directories used for active work:

 * [boards](./hardware/boards/) - The [KiCad](https://www.kicad.org/) board files for the active version of the hardware
 * [checklists](./hardware/checklists/) - Checklists to complete prior to board fabrication

In addition to these two main directories, there are also other directories that have the revision of the hardware as the name. These contain the finalized gerbers, KiCad source files, and any other needed files to facilitate manufacturing and production of that version of the hardware.

### The [squishy](./squishy/) Directory

This directory is the root of the Squishy python package. Each directory is a submodule within it. It is broken up into nine submodules:

 * [actions](./squishy/actions/) - Actions.
 * [applets](./squishy/applets/) - Packaged Applets.
 * [core](./squishy/core) - Support infrastructure for the rest of the package.
 * [gateware](./squishy/gateware/) - [Amaranth](https://github.com/amaranth-lang/amaranth) gateware files for use in Applets or other projects.
 * [gui](./squishy/gui/) - PySide/Qt based GUI.
 * [i18n](./squishy/i18n/) - Localization/internalization files.
 * [main](./squishy/main/) - Support code for running the package.
 * [misc](./squishy/misc/) - Miscellaneous support code.
 * [scsi](./squishy/scsi/) - SCSI Support library.

## Terminology

TODO