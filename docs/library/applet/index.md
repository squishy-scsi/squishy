# Applet API

```{toctree}
:hidden:

applet
device
```

```{todo}
Flesh this out
```

The following APIs are available for use within Squishy applets. They allow the applet
to register various components with the Squishy framework.

For details on how to write Squishy applets, see the [Applets Tutorial] for a walk-through.

## Applet Search Locations

Squishy searches for applets to load in two locations. The first being the built-in applets in the `squishy.applets` module, this is where all of the default applets that ship with Squishy are located.

The second location Squishy searches for applets in is partially platform dependent. Regardless of platform, the location is `.local/share/squishy/applets` within the current users home directory. Where this directory is depends on the system and it's configuration, but below are some common paths:

```{eval-rst}

.. tab:: Linux

	.. code-block:: console

		$HOME/.local/share/squishy/applets

.. tab:: macOS

	.. code-block:: console

		$HOME/.local/share/squishy/applets

.. tab:: Windows

	.. code-block:: console

		%USERPROFILE%/.local/share/squishy/applets


```

[Applets Tutorial]: ../../tutorials/applets/index.md
[CLI]: ./cli.md
