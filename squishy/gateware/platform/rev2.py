# SPDX-License-Identifier: BSD-3-Clause
from nmigen                            import *
from nmigen.build                      import *
from nmigen.vendor.lattice_ecp5        import LatticeECP5Platform
from nmigen_boards.resources.memory    import SPIFlashResources
from nmigen_boards.resources.user      import LEDResources
from nmigen_boards.resources.interface import UARTResource

from ...config                         import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER
from ...config                         import USB_MANUFACTURER, USB_PRODUCT, USB_SERIAL_NUMBER
from ...config                         import SCSI_VID

from ..core.clk                        import ECP5ClockDomainGenerator

class SquishyRev2(LatticeECP5Platform):
	device       = 'LFE5U-45F'
	package      = 'BG256'
	default_clk  = 'clk'
	toolchain    = 'Trellis'

	usb_vid      = USB_VID
	usb_pid_app  = USB_PID_APPLICATION
	usb_pid_boot = USB_PID_BOOTLOADER

	usb_mfr      = USB_MANUFACTURER
	usb_prod     = USB_PRODUCT
	usb_snum     = USB_SERIAL_NUMBER

	scsi_vid     = SCSI_VID

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

	resources  = [
		Resource('clk', 0,
			Pins('P1', dir = 'i'),
			Clock(16e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'SB_LVCMOS')
		),
		Resource('ulpi', 0,
			Subsignal('clk',
				Pins('P5', dir = 'i'),
				Clock(60e6)
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
				Pins('M1', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
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
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS'),
		),



		*SPIFlashResources(0,
			cs_n = 'R8', clk = 'N9', copi = 'T8', cipo = 'T7',

			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]


	connectors = [

	]
