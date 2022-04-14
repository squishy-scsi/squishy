# Squishy Applets

```{toctree}
:hidden:

analyzer
taperipper
api
```
Squishy allows for the development of modular pieces of combined code and [Amaranth HDL](https://github.com/amaranth-lang) gateware called an applet. It gives Squishy it's functionality and allows for the extension of said functionality and/or entirely new custom functionality.


There are currently two built-in applets, the [analyzer](./analyzer.md), and [taperipper](./taperipper.md) applets. With more built-in applets are planned for the future.

Squishy allows you to run your own custom applets, any python packages in the `SQUISHY_APPLETS` directory are attempted to be loaded as an applet, and then exposed to the user to allow them to invoke.

For more details on custom applets, see the [Custom Applet](../tutorials/applets/index.md) tutorial for a walkthrough of developing your own Squishy applet.
