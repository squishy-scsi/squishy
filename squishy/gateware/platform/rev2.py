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

	resources  = [ ]
	connectors = [ ]
