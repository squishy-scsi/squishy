# SPDX-License-Identifier: BSD-3-Clause

from .scsi import SCSIInterface
from .spi  import SPIInterface
from .uart import UARTInterface

from .pll  import ICE40ClockDomainGenerator
from .pll  import ECP5ClockDomainGenerator

__all__ = (
	'SCSIInterface',
	'SPIInterface',
	'UARTInterface',

	'ICE40ClockDomainGenerator',
	'ECP5ClockDomainGenerator',
)


__doc__ = '''\

This module contains the internal elaboratables that are used to construct the
gateware wrapper for Squishy applets. They are not intended to be manual instantiated
outside of the Squishy gateware wrapper, but they are available to do so if writing
custom gateware for Squishy hardware outside of the applet ecosystem.

As such, they are documented to allow for consumption, but do not hold any API stability
promises as they are still considered to be internal to the applet system and not
for general consumption.

It is roughly broken up into 3 submodules:
 * :py:mod:`squishy.gateware.core.pll` - PLL helpers for various FPGAs.
 * :py:mod:`squishy.gateware.core.spi` - Generic SPI interface.
 * :py:mod:`squishy.gateware.core.uart` - Debug UART.

''' # noqa: E101
