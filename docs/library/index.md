# Squishy as a Library

```{toctree}
:hidden:

applet/index
gateware/index
python/index

```

Squishy, along with being a standalone tool, is also an Torii HDL gateware library for interacting with SCSI, as well as a Python library for dealing with SCSI packets.

The [Applet] API is used to add new functionality to a Squishy device, it uses [Torii HDL] and leverages the [Gateware] and [Python] library components to provide a solid base to build whatever SCSI device one wants.

The [Gateware] documentation details all of the [Torii HDL] elaboratables and support code needed to integrate SCSI into your own Torii based project.

The [Python] documentation details all of the modules and support code for dealing with SCSI traffic on the host side, allow you to build python scripts that can interact with SCSI devices easily.

[Applet]: ./applet/index.md
[Gateware]: ./gateware/index.md
[Python]: ./python/index.md

[Torii HDL]: https://torii.shmdn.link/
