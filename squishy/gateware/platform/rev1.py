# SPDX-License-Identifier: BSD-3-Clause
from torii                               import *
from torii.build                         import *
from torii.platform.vendor.lattice.ice40 import ICE40Platform
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import LEDResources
from torii.platform.resources.interface  import UARTResource

from ...core.flash                       import FlashGeometry
from ..core                              import ICE40ClockDomainGenerator
from ..bootloader.rev1                   import Bootloader as iCE40Bootloader
from .resources                          import SCSIPhyResource
from .platform                           import SquishyPlatform

__doc__ = '''\

This is the torii platform definition for Squishy rev1 hardware, if you are using
Squishy rev1 as a generic FPGA development board, this is the platform you need to invoke.

Warning
-------
This platform is for specialized hardware and **must not** be used with any other
hardware other than the hardware it was designed for. This include any popular
development or eval boards.

Note
----
There are no official released of the Squishy rev1 hardware for purchase, you can build your
own, however it is recommended to start with the :py:class:`squishy.gateware.platform.rev2.SquishyRev2` hardware.


'''

class SquishyRev1(SquishyPlatform, ICE40Platform):
	'''
	Squishy hardware Revision 1

	This is the torii platform for the first revision of the Squishy hardware.
	It is based around the `Lattice iCE40-HX8K <https://www.latticesemi.com/iCE40>`_
	in the BG121 footprint.

	The design files for this version of the hardware can be found
	`in the git repo <https://github.com/squishy-scsi/hardware/tree/main/release/rev1>`_ under
	the `rev1` tree.

	'''

	device       = 'iCE40HX8K'
	package      = 'BG121'
	default_clk  = 'clk'
	toolchain    = 'IceStorm'

	revision     = 1.0

	clock_domain_generator = ICE40ClockDomainGenerator

	pll_config = {
		'freq'  : 1e8,
		'divr'  : 2,
		'divf'  : 49,
		'divq'  : 3,
		'frange': 1,
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

	bootloader_module = iCE40Bootloader

	resources = [
		Resource('clk', 0,
			Pins('L5', dir = 'i'),
			Clock(48e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('ulpi', 0,
			Subsignal('clk',
				Pins('G1', dir = 'i'),
				Clock(60e6),
				Attrs(GLOBAL = True)
			),
			Subsignal('data',
				Pins('E1 E2 F1 F2 G2 H1 H2 J1', dir = 'io')
			),
			Subsignal('dir',
				Pins('D1', dir = 'i')
			),
			Subsignal('nxt',
				Pins('D2', dir = 'i')
			),
			Subsignal('stp',
				Pins('C2', dir = 'o')
			),
			Subsignal('rst',
				PinsN('C1', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		SCSIPhyResource(0,
			ack = ('C11', 'B11'), atn = ('H11', 'H10'), bsy = ('E11', 'E10'),
			cd  = ('B5',  'A4' ), io  = ('B3',  'A2' ), msg = ('A8',  'B9' ),
			sel = ('B7',  'A6' ), req = ('B4',  'A3' ), rst = ('E9',  'D9' ),
			d0  = ('J11 G11 F11 D11 A10 C8 C9 B8', 'J10 G10 F10 D10 A11 C7 A9 A7'),
			dp0 = ('B6',  'A5' ),

			tp_en  = 'A1', tx_en  = 'K11', aa_en = 'G8',
			bsy_en = 'G9', sel_en = 'F9',  mr_en = 'E8',

			diff_sense = 'D7',

			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		*LEDResources(
			pins = [
				'L1', # [0] BLUE
				'L2', # [1] PINK
				'K3', # [2] WHITE
				'L3', # [3] PINK
				'K4'  # [4] BLUE
			],
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS'),
		),

		*SPIFlashResources(0,
			cs_n = 'K10', clk = 'L10', copi = 'K9', cipo = 'J9',

			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		UARTResource(0,
			rx = 'L7', tx = 'K7',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]

	connectors = []
