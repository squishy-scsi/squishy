# SPDX-License-Identifier: BSD-3-Clause

'''
This is the `Torii <https://torii.shmdn.link/>`_ platform definition for Squishy rev2 hardware.
If you are for some reason using Squishy rev2 as a general-purpose FPGA development board with
Torii, this is the platform you need to invoke.

Important
-------
This platform is for specialized hardware, as such it can not be used with any other hardware
than it was designed for. This includes any popular FPGA development or evaluation boards.

Note
----
There are no official releases of the Squishy rev2 hardware for purchase as it is currently
in the early engineering-validation-test phases, and will likely change drastically before
any are offered.

'''
import logging                          as log
from pathlib                            import Path

from torii                              import *
from torii.build                        import *
from torii.build.run                    import BuildProducts
from torii.platform.vendor.lattice.ecp5 import ECP5Platform
from torii.platform.resources.memory    import SDCardResources
from torii.platform.resources.user      import LEDResources
from torii.platform.resources.interface import ULPIResource

from .                                  import SquishyPlatform
from ...core.flash                      import Geometry as FlashGeometry
from ...core.config                     import ECP5PLLConfig, ECP5PLLOutput, FlashConfig

__all__ = (
	'SquishyRev2',
)


class Rev2ClockDomainGenerator(Elaboratable):
	'''
	Clock domain and PLL generator for Squishy rev2.

	This module sets up 3 primary clock domains, ``sync``, ``usb``, and ``scsi``. The first
	domain ``sync`` is the global core clock, the ``usb`` domain is a 60MHz domain originating
	from the ULPI PHY. The final domain ``scsi`` is the SCSI PHY domain.


	Attributes
	----------
	pll_locked : Signal
		An active high signal indicating if the PLL is locked and stable.
	'''

	def __init__(self) -> None:
		self.pll_locked = Signal()

	def elaborate(self, platform: 'SquishyRev2') -> Module:
		m = Module()

		# Set up our domains
		m.domains.usb  = ClockDomain()
		m.domains.sync = ClockDomain()
		m.domains.scsi = ClockDomain()

		# The ECP5 PLL and clock output configs
		# TODO(aki): We don't need them at the moment but cascaded PLLs might come in handy
		pll_cfg: ECP5PLLConfig = platform.pll_cfg

		pll_sync_cfg = pll_cfg.clkp
		# TODO(aki): Handle secondary, tertiary, and quaternary PLL outputs

		# The PLL output clocks
		pll_sync_clk = Signal()

		m.submodules.pll = Instance(
			'EHXPLLL',

			i_CLKI    = platform.request(platform.default_clk, dir = 'i'),

			o_CLKOP   = pll_sync_clk,
			i_CLKFB   = pll_sync_clk,
			i_ENCLKOP = Const(0),
			o_LOCK    = self.pll_locked,

			i_RST       = Const(0),
			i_STDBY     = Const(0),

			i_PHASESEL0    = Const(0),
			i_PHASESEL1    = Const(0),
			i_PHASEDIR     = Const(1),
			i_PHASESTEP    = Const(1),
			i_PHASELOADREG = Const(1),
			i_PLLWAKESYNC  = Const(0),

			# Params
			p_PLLRST_ENA      = 'DISABLED',
			p_INTFB_WAKE      = 'DISABLED',
			p_STDBY_ENABLE    = 'DISABLED',
			p_DPHASE_SOURCE   = 'DISABLED',
			p_OUTDIVIDER_MUXA = 'DIVA',
			p_OUTDIVIDER_MUXB = 'DIVB',
			p_OUTDIVIDER_MUXC = 'DIVC',
			p_OUTDIVIDER_MUXD = 'DIVD',
			p_FEEDBK_PATH     = 'CLKOP',

			p_CLKI_DIV        = pll_cfg.clki_div,
			p_CLKFB_DIV       = pll_cfg.clkfb_div,

			p_CLKOP_DIV       = pll_sync_cfg.clk_div,
			p_CLKOP_ENABLE    = 'ENABLED',
			p_CLKOP_CPHASE    = Const(pll_sync_cfg.cphase),
			p_CLKOP_FPHASE    = Const(pll_sync_cfg.fphase),

			# Attributes for synth
			a_FREQUENCY_PIN_CLKI     = str(pll_cfg.ifreq),
			a_FREQUENCY_PIN_CLKOP    = str(pll_sync_cfg.ofreq),
			a_ICP_CURRENT            = '12',
			a_LPF_RESISTOR           = '8',
			a_MFG_ENABLE_FILTEROPAMP = '1',
			a_MFG_GMCREF_SEL         = '2',
		)

		# Set up clock constraints
		platform.add_clock_constraint(pll_sync_clk, pll_sync_cfg.ofreq * 1e6)

		# Hook up needed PLL outputs
		m.d.comb += [
			# Hold domain in reset until the PLL stabilizes
			ResetSignal('sync').eq(~self.pll_locked),

			# Wiggle the clock
			ClockSignal('sync').eq(pll_sync_clk)
		]

		return m

class SquishyRev2(SquishyPlatform, ECP5Platform):
	'''
	Squishy hardware, Revision 2.

	This `Torii <https://torii.shmdn.link/>`_ platform is for the first revision of the Squishy SCSI hardware. It
	is based on the `Lattice ECP5-5G <https://www.latticesemi.com/Products/FPGAandCPLD/ECP5>`_ Specifically the
	``LFE5UM5G-45F`` and is built to be as flexible as possible, as such it is split between the main board, the
	SCSI PHY, and the various connectors boards.

	The hardware `design files <https://github.com/squishy-scsi/hardware/tree/main/release/rev2-evt>`_ can be
	found in the hardware repository on `GitHub <https://github.com/squishy-scsi/hardware>`_  under
	the ``release/rev2-evt`` tree.


	Warning
	-------
	Squishy rev2 is currently in engineering-validation-test, and is unstable, the hardware
	may change and new, possibly fatal errata may be found at any time. Use with caution.

	'''

	device           = 'LFE5UM5G-45F'
	speed            = '8'
	package          = 'BG381'
	default_clk      = 'clk'
	toolchain        = 'Trellis'
	bitstream_suffix = 'bit'

	revision     = (2, 0)

	flash = FlashConfig(
		geometry = FlashGeometry(
			size       = 8388608, # 8MiB
			page_size  = 256,
			erase_size = 4096,    # 4KiB
			slot_size  = 2097152, # 2MiB
			addr_width = 24
		),
		commands = {
			'erase': 0x20,
		}
	)

	# generated with `ecppll -i 100 -o 400 -f /dev/stdout`
	pll_cfg = ECP5PLLConfig(
		ifreq     = 100,
		clki_div  = 1,
		clkfb_div = 4,
		# Primary `sync` clock, 400 is too high but as a placeholder it works
		clkp = ECP5PLLOutput(
			ofreq   = 400,
			clk_div = 1,
			cphase  = 0,
			fphase  = 0,
		)
	)

	clk_domain_generator = Rev2ClockDomainGenerator

	# Set DFU alt-mode slot for the ephemeral endpoint
	ephemeral_slot = 3

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
			Subsignal('copi',     Pins('W2', dir = 'io')),
			Subsignal('cipo',     Pins('V2', dir = 'io')),
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

		ULPIResource('ulpi', 0,
			#        D0  D1  D2  D3  D4  D5  D6  D7
			data = 'R18 R20 P19 P20 N20 N19 M20 M19',
			clk  = 'P18', clk_dir = 'i', # NOTE(aki): This /not technically/ a clock input pin, oops
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

	connectors = []

	def __init__(self) -> None:
		# Force us to always use the FOSS
		super().__init__(toolchain = 'Trellis')

	def pack_artifact(self,  artifact: bytes) -> bytes:
		'''
		Pack bitstream/gateware into device artifact.

		Parameters
		----------
		artifact : bytes
			The input data of the result of gateware elaboration, typically
			the raw FPGA bitstream file.

		Returns
		-------
		bytes
			The resulting packed artifact for DFU upload.

		'''

		log.warning('TODO: pack_artifact() for rev2')
		return artifact


	def build_image(self, name: str, build_dir: Path, boot_name: str, products: BuildProducts) -> Path:
		'''
		Build multi-boot compatible flash image to provision onto the device.

		Parameters
		----------
		name : str
			The name of the flash image to produce.

		build_dir : Path
			Output directory for the finalized flash image.

		boot_name: str
			The name of the bootloader in the build products

		products : BuildProducts
			The resulting build products from the bootloader build.

		Returns
		-------
		Path
			The path to the resulting image file.
		'''

		log.warning('TODO: build_image() for rev2')
		return build_dir
