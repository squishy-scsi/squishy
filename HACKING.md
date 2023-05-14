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
 * [squishy](./squishy/) - The actual source for the Squishy package itself


Each directory has it's own layout in an attempt to be as logical as possible. However the squishy directory might need some possible further explanation.

### The [squishy](./squishy/) Directory

This directory is the root of the Squishy python package. Each directory is a submodule within it. It is broken up into nine submodules:

 * [actions](./squishy/actions/) - Actions used on the command line.
 * [applets](./squishy/applets/) - Applets that are built-in to squishy.
 * [core](./squishy/core) - Support infrastructure for the rest of the package.
 * [gateware](./squishy/gateware/) - [Torii](https://github.com/shrine-maiden-heavy-industries/torii-hdl) gateware files for use in Applets or other projects.
 * [scsi](./squishy/scsi/) - SCSI Support library.

## Terminology

TODO
