# Squishy - Supervisor Firmware

> [!CAUTION]
> This documentation is ***really*** rough and incomplete, it will be
> eventually rolled into the [main documentation](https://docs.scsi.moe),
> but only once it's been stabilized.

This is the firmware that runs on the supervisor MCU on the squishy rev2 board, which is responsible for handling programming the FPGA and ensuring it can always boot into backup bootloader gateware.

## Building

To build the firmware you need a handful of things:

* meson >= 1.4.0
* ninja
* and a GCC `arm-none-eabi` cross compiler toolchain


To build the firmware, create a build directory (we'll call it `$BUILD`) and then invoke `meson` passing the toolchain file, like so:

```
$ meson setup --cross-file contrib/arm-none-eabi.meson $BUILD firmware
```

With that all done and happy, you can then build the firmware ELF with `ninja -C build`.
