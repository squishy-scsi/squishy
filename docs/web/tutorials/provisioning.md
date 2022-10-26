# Provisioning a New Device

```{toctree}
:hidden:

```

When you first build a squishy, or if the flash on your existing squishy gets corrupted, you will need to provision the device again. This is done by flashing a special image into the flash that contains the bootloader and stub bitstreams to ensure DFU works properly.

## Generating the Initial Image

To generate the initial image, we run squishy with the `provision` command like so:

```{eval-rst}
.. code-block:: console

	(squishy.venv) $ squishy provision --build-only --whole-device
```
The `--build-only` argument tells the `provision` command to build the but not program the image to a device, this means you can build it without a Squishy attached or for a blank Squishy.

The `--whole-device` argument tells `provision` to build the bootloader and bake the special device image that is to be flashed onto Squishy.

The resulting file `squishy-unified.bin` can then be flashed onto the SPI flash of the Squishy unit.

## Flashing the Image

To write the image to the Squishy device, you can hook up to the SPI header on the board using any capable tool and flash the whole `squishy-unified.bin` image. Once the device is then reset and able to read the new image, it will start in the bootloader waiting for an applet to be flashed to the device via the `squishy` utility or `dfu-util`.
