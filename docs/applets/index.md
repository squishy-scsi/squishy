# Applets

```{toctree}
:hidden:

analyzer
```

```{todo}
Flesh this section out
```

Squishy allows for the development of modular pieces of combined code and [Torii HDL] gateware called an applet. It gives Squishy it's functionality and allows for the extension of said functionality and/or entirely new custom functionality.

There is currently one built-in applet, the [analyzer], with more built-in applets are planned for the future.

Squishy allows you to run your own custom applets, any python packages in the `SQUISHY_APPLETS` directory are attempted to be loaded as an applet, and then exposed to the user to allow them to invoke.

For more details on custom applets, see the [Custom Applet] tutorial for a walkthrough of developing your own Squishy applet.

[Custom Applet]: ../tutorials/applets/index.md
[analyzer]: ./analyzer.md
[Torii HDL]: https://github.com/shrine-maiden-heavy-industries/torii-hdl
