# SPDX-License-Identifier: BSD-3-Clause
from torii                              import *
from torii.build                        import *
from torii.platform.vendor.lattice_ecp5 import LatticeECP5Platform
from torii.platform.resources.memory    import SPIFlashResources
from torii.platform.resources.user      import LEDResources
from torii.platform.resources.interface import UARTResource

from ...config                          import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER
from ...config                          import USB_MANUFACTURER, USB_PRODUCT
from ...config                          import SCSI_VID

from ...core.flash                      import FlashGeometry

from ..core                             import ECP5ClockDomainGenerator
from .mixins                            import SquishyCacheMixin

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

class SquishyRev2(SquishyCacheMixin, LatticeECP5Platform):
	'''Squishy hardware Revision 2

	This is the torii platform for the first revision of the Squishy hardware.
	It is based around the `Lattice ECP5-5G LFE5UM5G-45F <https://www.latticesemi.com/Products/FPGAandCPLD/ECP5>`_
	in the BG381 footprint.

	The design files for this version of the hardware can be found
	`in the git repo <https://github.com/lethalbit/squishy/tree/main/hardware/boards/squishy>`_ under
	the `hardware/boards/squishy` tree.


	'''

	device       = 'LFE5UM5G-45F'
	speed        = '8'
	package      = 'BG381'
	default_clk  = 'clk'
	toolchain    = 'Trellis'

	usb_vid      = USB_VID
	usb_pid_app  = USB_PID_APPLICATION
	usb_pid_boot = USB_PID_BOOTLOADER

	usb_mfr      = USB_MANUFACTURER
	usb_prod     = USB_PRODUCT

	scsi_vid     = SCSI_VID

	revision     = 2

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
			Pins('P1', dir = 'i'),
			Clock(16e6),
			Attrs(IO_TYPE = 'LVCMOS33')
		),

		Resource('tio', 0,
			Subsignal('trigger',
				Pins('N16', dir = 'io')
			),
			Subsignal('refclk',
				Pins('M15', dir = 'io')
			),
			Attrs(IO_TYPE = 'LVCMOS33')
		),

		Resource('ulpi', 0,
			Subsignal('clk',
				Pins('P5', dir = 'i'),
				Clock(60e6),
				Attrs(GLOBAL = True),
			),
			Subsignal('data',
				Pins('P1 R2 R1 T2 T3 R3 T4 R4', dir = 'io')
			),
			Subsignal('dir',
				Pins('N1', dir = 'i')
			),
			Subsignal('nxt',
				Pins('P2', dir = 'i')
			),
			Subsignal('stp',
				Pins('M2', dir = 'o')
			),
			Subsignal('rst',
				PinsN('M1', dir = 'o')
			),

			Attrs(IO_TYPE = 'LVCMOS33')
		),

		Resource('termpwr', 0,
			Subsignal('adc_rst',
				PinsN('B2', dir = 'o')
			),
			Subsignal('sda',
				Pins('C2', dir = 'io')
			),
			Subsignal('scl',
				Pins('B1', dir = 'oe')
			),

			Attrs(IO_TYPE = 'LVCMOS33')
		),

		*LEDResources(
			pins = [
				'R7', # [4] White
				'T6', # [5] White
				'R6', # [6] Pink
				'P8', # [7] Pink
				'P7', # [8] Blue
				'P6'  # [9] Blue
			],
			attrs = Attrs(IO_TYPE = 'LVCMOS33'),
		),


		*SPIFlashResources(0,
			cs_n = 'R8', clk = 'N9', copi = 'T8', cipo = 'T7',

			attrs = Attrs(IO_TYPE = 'LVCMOS33')
		),

		UARTResource(0,
			rx = 'T14', tx = 'R14',
			attrs = Attrs(IO_TYPE = 'LVCMOS33')
		),
	]


	connectors = [

	]
