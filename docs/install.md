# Installation

```{warning}
The following instructions are a work-in-progress and may not be entirely up to date.
```

Squishy is a python application that can be installed via [`pip`],  either from the [git repository] or via a [wheel] package.

## System Requirements

Squishy is officially supported on most Linux distributions, the primary one being [Arch Linux] and variants there of. However other Linux distributions are supported as well.

Support for Microsoft Windows is preliminary, and due to lack of testing and development resources official support is currently not possible. But effort to make it as painless as possible to use on this platform is in-progress.

Support for Apple macOS is also unofficial, however due to its similarity to Linux and Unix-like operating systems, using Squishy on macOS should be just as painless as it is on Linux. Official support for macOS and other BSD-Family operating systems is planned.

Regardless of the operating system, there are some core dependencies that Squishy requires. This includes Python >= 3.10, [Yosys] >= 0.39, and [nextpnr] >= 0.7.

Squishy has been tested with [CPython], but might possibly run under [PyPy].

## Installing Prerequisites

Prior to installing Squishy, you must install all of its prerequisites and requirements.

### Installing Python

First off, install `python` and `pip` onto your system if the're not there already. It is also recommended to upgrade `pip` if not already to ensure all the steps work as expected.

```{eval-rst}
.. tab:: Arch-like

	.. code-block:: console

		$ sudo pacman -S python python-pip

.. tab:: Other Linux

	.. warning:: These instructions may be incorrect or incomplete!

	.. tab:: Debian-Like

		For `Debian <https://www.debian.org/>`_ based systems, use ``apt`` to install ``python3`` and ``python3-pip``

		.. code-block:: console

			$ sudo apt install python3 python3-pip

	.. tab:: Fedora-like

		For `Fedora <https://getfedora.org/>`_ and other ``dnf`` based systems,

		.. code-block:: console

			$ sudo dnf install python3 python3-pip

.. tab:: macOS

	Install `Homebrew <https://brew.sh/>`_ if not done already, then install the requirements.

	.. code-block:: console

		$ brew install python

.. tab:: Windows

	.. warning:: These instructions may be incorrect or incomplete!

	Download the latest Python installer from the `python downloads <https://www.python.org/downloads/>`_ page.

	Follow the instructions and ensure that the installer installs ``pip`` and puts the python executable in your ``%PATH%``

```
At this point, you may want to create a virtual environment for installing Squishy into:

```{eval-rst}
.. code-block:: console

	$ python -m venv squishy.venv
```

```{note}
If your python install doesn't have the `venv` module by default, then you will need to also install the python `virtualenv` package
```

You can then activate the virtual environment with:
```{eval-rst}
.. tab:: Arch-like

	.. code-block:: console

		$ . squishy.venv/bin/activate

.. tab:: Other Linux

	.. code-block:: console

		$ . squishy.venv/bin/activate

.. tab:: macOS

	.. code-block:: console

		$ . squishy.venv/bin/activate

.. tab:: Windows

	.. code-block:: console

		$ call squishy.venv/Scripts/activate.bat
```

### Installing Yosys and nextpnr

Next, you need to install [`yosys`] and [`nextpnr`] onto your system if it is not there already.

#### Native Install

The next option is to do a native install of the toolchain.

```{eval-rst}
.. tab:: Arch-like

	On Arch Linux and Arch-likes, you can install nightly packages which are located in the `AUR <https://aur.archlinux.org/>`_ with an AUR helper or using ``makepkg`` directly.


	Via an AUR helper like ``yay``

	.. code-block:: console

		$ yay -S yosys-nightly nextpnr-ice40-nightly nextpnr-ecp5-nightly

	Via ``makepkg`` directly

	.. code-block:: console

		$ git clone https://aur.archlinux.org/yosys-nightly.git
		$ git clone https://aur.archlinux.org/prjtrellis-nightly.git
		$ git clone https://aur.archlinux.org/icestorm-nightly.git
		$ git clone https://aur.archlinux.org/nextpnr-ecp5-nightly.git
		$ git clone https://aur.archlinux.org/nextpnr-ice40-nightly.git
		$ (cd yosys-nightly && makepkg -sic)
		$ (cd prjtrellis-nightly && makepkg -sic)
		$ (cd icestorm-nightly && makepkg -sic)
		$ (cd nextpnr-ecp5-nightly && makepkg -sic)
		$ (cd nextpnr-ice40-nightly && makepkg -sic)


.. tab:: Other Linux

	.. warning:: These instructions may be incorrect or incomplete!

	With other Linux distributions, it is recommended to use the `OSS Cad Suite <https://github.com/YosysHQ/oss-cad-suite-build>`_ nightly build. It provides a full environment of all the tools needed built on a nightly basis.

	Simply download the latest `release <https://github.com/YosysHQ/oss-cad-suite-build/releases>`_ for your architecture, extract it to a good home, and then add it to your ``$PATH``

	.. code-block:: console

		$ curl -LOJ https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-07-02/oss-cad-suite-linux-x64-20240702.tgz
		$ tar xfv oss-cad-suite-linux-x64-20240702.tgz
		$ export PATH="`pwd`/oss-cad-suite/bin:$PATH"


.. tab:: macOS

	For macOS systems, it is recommended to use the YoWASP distribution of the toolchain. However if you want to use the native tools, and you are using an Intel based Mac, then the `OSS Cad Suite <https://github.com/YosysHQ/oss-cad-suite-build>`_ has nightly builds for x86_64 versions of Darwin.

	Simply download the latest `release <https://github.com/YosysHQ/oss-cad-suite-build/releases>`_ for your architecture, extract it to a good home, and then add it to your ``$PATH``

	.. code-block:: console

		$ curl -LOJ https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-07-02/oss-cad-suite-darwin-x64-20240702.tgz
		$ tar xfv oss-cad-suite-darwin-x64-20240702.tgz
		$ export PATH="`pwd`/oss-cad-suite/bin:$PATH"

.. tab:: Windows

	.. warning:: These instructions may be incorrect or incomplete!

	For Windows systems, it is recommended to use the YoWASP distribution of the toolchain. However if you want to use the native tools, and you are using an Intel based PC, then the `OSS Cad Suite <https://github.com/YosysHQ/oss-cad-suite-build>`_ has nightly builds for x86_64 versions of Windows.

	Simply download the latest `release <https://github.com/YosysHQ/oss-cad-suite-build/releases>`_ for your architecture, extract it to a good home, and then add it to your ``%PATH%``

	.. code-block:: console

		$ call %cd%\oss-cad-suite\environment.bat

```

## Installing Squishy

```{eval-rst}
.. note::

	Due to some of squishy's dependencies, we can not publish a PyPi package at the moment.
```

Once all of the prerequisites are installed, you can finally install squishy into the virtual environment like so:

```{eval-rst}
.. code-block:: console

	(squishy.venv) $ pip install 'squishy @ git+https://github.com/squishy-scsi/squishy.git'
```

After that, check to make sure you have the `squishy` command:

```{eval-rst}
.. code-block:: console

	(squishy.venv) $ squishy --help
```

Now you can view the [Getting Started] page and start to use Squishy.

[`pip`]: https://pypi.org/project/pip/
[git repository]: https://github.com/squishy-scsi/squishy
[wheel]: https://pypi.org/project/wheel/
[Arch Linux]: https://archlinux.org/
[Yosys]: https://github.com/YosysHQ/yosys
[nextpnr]: https://github.com/YosysHQ/nextpnr
[CPython]: https://www.python.org/
[PyPy]: https://www.pypy.org/
[`yosys`]: https://github.com/YosysHQ/yosys
[`nextpnr`]: https://github.com/YosysHQ/nextpnr
[Getting Started]: ./getting_started.md
