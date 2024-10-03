# SPDX-License-Identifier: BSD-3-Clause
from torii                              import *
from torii.build                        import *
from torii.platform.vendor.lattice.ecp5 import ECP5Platform
from torii.platform.resources.memory    import SDCardResources
from torii.platform.resources.user      import LEDResources
from torii.platform.resources.interface import ULPIResource

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

	# generated with `ecppll -i 100 -o 400 -f /dev/stdout`
	pll_config = {
		'freq'     : 4e8,
		'ifreq'    : 100,
		'ofreq'    : 400,
		'clki_div' : 1,
		'clkop_div': 1,
		'clkfb_div': 4,
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

		# Ext Trigger
		Resource('trig', 0,
			Subsignal('trigger', PinsN('H1', dir = 'io')),
			Attrs(IO_TYPE = 'LVCMOS33')
		),

		*SDCardResources('sd_card', 0,
			clk = 'M1', cmd = 'L2', cd = 'N2',
			dat0 = 'M3', dat1 = 'N1', dat2 = 'L3', dat3 = 'L1',
			attrs = Attrs(IO_TYPE = 'LVCMOS33')
		),

		# Supervisor bus
		Resource('supervisor',  0,
			# NOTE(aki): The clk can be driven by the MCU *or* the FPGA, which
			# might cause issues, we need to have an interlock
			Subsignal('clk',      Pins('U2', dir = 'io')),
			Subsignal('copi',     Pins('W2', dir = 'i')),
			Subsignal('cipo',     Pins('V2', dir = 'o')),
			Subsignal('attn',    PinsN('T2', dir = 'i')), # This is the CS for the FPGA
			Subsignal('psram',   PinsN('Y2', dir = 'o')), # The bitstram cache PSRAM CS from our side
			Subsignal('su_attn',  Pins('W1', dir = 'o')),
			Subsignal('dfu_trg', PinsN('V1', dir = 'o')),

			Attrs(IO_TYPE = 'LVCMOS33')
		),

		# Status LEDs
		*LEDResources(
			# LED Num: 0  1  2  3  4
			pins   = 'K4 K5 L4 L5 M5',
			invert = True,
			attrs  = Attrs(IO_TYPE = 'LVCMOS33')
		),

		# HyperRAM Cache, This is a weird 2-banked w/ 2 chips per bank layout
		Resource('ram', 0,
			#                         DQ0 DQ1 DQ2 DQ3 DQ4 DQ5 DQ6 DQ7
			Subsignal('dq_odd', Pins('J18 J17 H20 J19 J20 K20 K19 K18', dir = 'io')),
			Subsignal('dq_evn', Pins('E18 E17 D18 E19 E20 F19 F18 F17', dir = 'io')),
			#                          CS0 CS1
			Subsignal('cs_odd', PinsN('G19 G18', dir = 'o')),
			Subsignal('cs_evn', PinsN('D20 C18', dir = 'o')),

			Subsignal('clk_odd', DiffPairs('F20', 'G20', dir = 'o')),
			Subsignal('clk_evn', DiffPairs('C20', 'D19', dir = 'o')),

			Subsignal('rwds', Pins('H18', dir = 'io')),
			Subsignal('rst', Pins('D17', dir = 'o')),

			Attrs(IO_TYPE = 'LVCMOS18', SLEWRATE = 'FAST')
		),

		ULPIResource('usb2', 0,
			#        D0  D1  D2  D3  D4  D5  D6  D7
			data = 'R18 R20 P19 P20 N20 N19 M20 M19',
			clk  = 'P18', clk_dir = 'i',
			dir  = 'T19',
			nxt  = 'T20',
			stp  = 'U20',
			rst  = 'U19', rst_invert = True,
			# Make the signal edges be sharp enough to cause me to bleed
			attrs = Attrs(IO_TYPE = 'LVCMOS33', SLEWRATE = 'FAST')
		),
		# The USB 3.1 Super-Speed is bound to DCU1 Chan1 (W17 W18)
		Resource('usb_pd',  0,
			Subsignal('scl', Pins('M18', dir = 'io')),
			# Errata: The schematic has a typo calling it `PD_SCA` rather than `PD_SDA`
			Subsignal('sda', Pins('N17', dir = 'io')),
			Subsignal('pol', Pins('N18', dir = 'o')),
			Attrs(IO_TYPE = 'LVCMOS33')
		),

		# This will be replaced with a proper Squishy SCSI-PHY resource eventually:tm:
		Resource('scsi_phy', 0,
			# SCSI Bus              #      0  1  2  3  4  5  6   7  P0
			Subsignal('data_lower', Pins('B5 A6 B6 A8 B8 A9 B9 A10 B10', dir = 'io')),
			#                               8   9  10  11 12 13 14 15 P1
			Subsignal('data_upper', Pins('A18 B18 A19 B19 A2 B1 A4 B2 A5', dir = 'io')),
			Subsignal('atn', Pins('B11', dir = 'io')),
			Subsignal('bsy', Pins('A11', dir = 'io')),
			Subsignal('ack', Pins('C11', dir = 'io')),
			Subsignal('rst', Pins('A13', dir = 'io')),
			Subsignal('msg', Pins('B13', dir = 'io')),
			Subsignal('sel', Pins('A15', dir = 'io')),
			Subsignal('cd',  Pins('B15', dir = 'io')),
			Subsignal('req', Pins('A17', dir = 'io')),
			Subsignal('io',  Pins('B16', dir = 'io')),

			# PHY Direction Signals
			Subsignal('data_lower_dir', Pins('B3',  dir = 'o')), # DB[00..07], DP0
			Subsignal('data_upper_dir', Pins('C1',  dir = 'o')), # DB[08..15], DP1
			Subsignal('trgt_dir',       Pins('B17', dir = 'o')), # C/D, I/O, MSG, REQ
			Subsignal('init_dir',       Pins('B12', dir = 'o')), # ACK, ATN
			Subsignal('bsy_dir',        Pins('A12', dir = 'o')), # BSY
			Subsignal('rst_dir',        Pins('A14', dir = 'o')), # RST
			Subsignal('sel_dir',        Pins('A16', dir = 'o')), # SEL

			# PHY Control/Supervisory signals
			Subsignal('scl',        Pins('F2', dir = 'io')),
			Subsignal('sda',        Pins('E1', dir = 'io')),
			Subsignal('termpwr_en', Pins('D1', dir = 'o')),
			Subsignal('prsnt',     PinsN('E2', dir = 'i')),
			# Extra Signals
			Subsignal('ls_ctrl', Pins('C2 C3 C16 C17 C14 C15', dir = 'io')), # LS_CTRL[0..5] Low-speed control lines
			# This /might/ go better with the ADC?
			Subsignal('pwr_en',    PinsN('H2', dir = 'o')),

			Attrs(IO_TYPE = 'LVCMOS33', SLEWRATE = 'FAST')
		),

		# SCSI PHY Current ADC
		Resource('phy_adc', 0,
			Subsignal('clk',  Pins('F1', dir = 'o')),
			Subsignal('dat',  Pins('G2', dir = 'i')),
			Subsignal('chan', Pins('G1', dir = 'o')),
			Attrs(IO_TYPE = 'LVCMOS33')
		),
	]


	connectors = [

	]
