# SPDX-License-Identifier: BSD-3-Clause
from torii                              import *
from torii.build                        import *
from torii.platform.vendor.lattice.ecp5 import ECP5Platform
from torii.platform.resources.memory    import SPIFlashResources
from torii.platform.resources.user      import LEDResources
from torii.platform.resources.interface import UARTResource

from ...core.flash                      import FlashGeometry
from ..core                             import ECP5ClockDomainGenerator
from .platform                          import SquishyPlatform

__doc__ = '''\

This is the torii platform definition for Squishy rev2 hardware, if you are using
Squishy rev2 as a generic FPGA development board, this is the platform you need to invoke.

Warning
-------
This platform is for specialized hardware and **must not** be used with any other
hardware other than the hardware it was designed for. This include any popular
development or eval boards.

Note
----
There are no official released of the Squishy rev2 hardware for purchase at the moment. You can
build your own, or keep an eye out for when the campaign goes live.

'''

class SquishyRev2(SquishyPlatform, ECP5Platform):
	'''
	Squishy hardware Revision 2

	This is the torii platform for the first revision of the Squishy hardware.
	It is based around the `Lattice ECP5-5G LFE5UM5G-45F <https://www.latticesemi.com/Products/FPGAandCPLD/ECP5>`_
	in the BG381 footprint.

	The design files for this version of the hardware can be found
	`in the git repo <https://github.com/squishy-scsi/hardware/tree/main/boards/squishy>`_ under
	the `boards/squishy` tree.


	'''

	device       = 'LFE5UM5G-45F'
	speed        = '8'
	package      = 'BG381'
	default_clk  = 'clk'
	toolchain    = 'Trellis'

	revision     = 2.0

	clock_domain_generator = ECP5ClockDomainGenerator

	# generated with `ecppll -i 16 -o 400 -f /dev/stdout`
	pll_config = {
		'freq'     : 4e8,
		'ifreq'    : 16,
		'ofreq'    : 400,
		'clki_div' : 1,
		'clkop_div': 1,
		'clkfb_div': 25,
	}

	flash = {
		'geometry': FlashGeometry(
			size       = 8388608, # 8MiB
			page_size  = 256,
			erase_size = 4096,    # 4KiB
			addr_width = 24
		).init_slots(device = device),
		'commands': {
			'erase': 0x20,
		}
	}

	bootloader_module = None

	resources  = [
		Resource('clk', 0,
			DiffPairs('P3', 'P4', dir = 'i'),
			Clock(100e6),
			Attrs(IO_TYPE = 'LVDS')
		),
	]


	connectors = [

	]
