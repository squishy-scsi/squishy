# Installation

**NOTE:** The following instructions are a work-in-progress and may not be entirely up to date.

## System Requirements

Squishy requires Python 3.8 or newer, It has been tested with [CPython](https://www.python.org/).

[Yosys](https://github.com/YosysHQ/yosys) 0.10 or newer is also required, along with [Amaranth HDL](https://github.com/amaranth-lang/amaranth).

## Installing Prerequisites

```{eval-rst}
.. platform-picker::
	.. platform-choice:: arch
		:title: Arch Linux

		Install Python, pip, and yosys by running:

		.. code-block:: console

		  $ sudo pacman -S python python-pip yosys

		You may also use the `nightly version of Yosys <https://aur.archlinux.org/packages/yosys-nightly>`_ from the `AUR <https://aur.archlinux.org/>`_.

		.. code-block:: console

			$ git clone https://aur.archlinux.org/yosys-nightly.git
			$ cd yosys-nightly
			$ makepkg -sic

		For targeting Squishy rev1 you also need nextpnr-ice40, this can be done by using the `nextpnr-ice40-nightly PKGBUILD <https://aur.archlinux.org/packages/nextpnr-ice40-nightly>`_ from the `AUR <https://aur.archlinux.org/>`_.

		.. code-block:: console

			$ git clone https://aur.archlinux.org/nextpnr-ice40-nightly.git
			$ cd nextpnr-ice40-nightly
			$ makepkg -sic

		For targeting Squishy rev2 you also need nextpnr-ecp5, this can be done by using the `nextpnr-ecp5-nightly PKGBUILD <https://aur.archlinux.org/packages/nextpnr-ecp5-nightly>`_ from the `AUR <https://aur.archlinux.org/>`_.

		.. code-block:: console

			$ git clone https://aur.archlinux.org/nextpnr-ecp5-nightly.git
			$ cd nextpnr-ecp5-nightly
			$ makepkg -sic


	.. platform-choice:: linux
		:title: Other Linux
		
		.. todo::

			Write this section

	.. platform-choice:: macos
		:title: macOS
			
		.. todo::

			Write this section


	.. platform-choice:: windows
		:title: Windows
		
		
		.. todo::

			Write this section



```

## Installing Dependencies (Normal Usage)

```{eval-rst}
.. platform-picker::
	.. platform-choice:: arch
		:title: Arch Linux

		All of the dependencies that Squishy requires are in the setup.py, however if you wish to install them manually, you can.

		The following packages can be installed from the Arch Linux repos:

		.. code-block:: console

			$ sudo pacman -S python-jinja python-construct python-pyusb python-tqdm  

		Then install Amaranth HDL from source if not installed already:

		.. code-block:: console

			$ pip install git+https://github.com/amaranth-lang/amaranth.git@main
			$ pip install git+https://github.com/amaranth-lang/amaranth-boards.git@main
			$ pip install git+https://github.com/amaranth-lang/amaranth-stdio.git@main


		Finally, install the python-usb-protocol and LUNA forks

		.. code-block:: console

			$ pip install git+https://github.com/dragonmux/python-usb-protocol.git@main
			$ pip install git+https://github.com/shrine-maiden-heavy-industries/luna.git@amaranth#egg=luna-0.1.0.dev0


	.. platform-choice:: linux
		:title: Other Linux
		
		.. todo::

			Write this section

	.. platform-choice:: macos
		:title: macOS
			
		.. todo::

			Write this section

	.. platform-choice:: windows
		:title: Windows
		
		.. todo::

			Write this section

```

## Installing Dependencies (GUI - Optional)

```{eval-rst}
.. platform-picker::
	.. platform-choice:: arch
		:title: Arch Linux

		To use the Squishy GUI, only PiSide2 is needed in addition to the normal dependencies and can be installed as follows:

		.. code-block:: console

 			$ sudo pacman -S pyside2

	.. platform-choice:: linux
		:title: Other Linux
			
		.. todo::

			Write this section

	.. platform-choice:: macos
		:title: macOS
		
		.. todo::

			Write this section

	.. platform-choice:: windows
		:title: Windows
		
		.. todo::

			Write this section


```

## Installing Dependencies (Firmware Build - Optional)

There is also the ability in squishy to build machine code components, which need [Meson](https://mesonbuild.com/), [Ninja](https://ninja-build.org/), and optionally a cross-compiler toolchain.


```{eval-rst}
.. platform-picker::
	.. platform-choice:: arch
		:title: Arch Linux

		Meson and Ninja can be installed from the repos as follows:

		.. code-block:: console

 			$ sudo pacman -S meson ninja

	.. platform-choice:: linux
		:title: Other Linux
		
		.. todo::

			Write this section

	.. platform-choice:: macos
		:title: macOS
		
		.. todo::

			Write this section

	.. platform-choice:: windows
		:title: Windows
		
		.. todo::

			Write this section


```

## Installing Squishy

```{eval-rst}
.. platform-picker::
	.. platform-choice:: linux
		:title: Linux
		
		Install a non-editable snapshot by running the following:

		.. code-block:: console

 			$ pip3 install --user 'git+https://github.com/lethalbit/squishy.git'

 		To install an editable development snapshot, run the following:

 		.. code-block:: console

 			$ git clone https://github.com/lethalbit/squishy.git
 			$ cd squishy
 			$ pip3 install --user --editable .


	.. platform-choice:: macos
		:title: macOS
		
		TODO

	.. platform-choice:: windows
		:title: Windows
		
		TODO


```
