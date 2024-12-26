# SPDX-License-Identifier: BSD-3-Clause

'''
This is the `Torii <https://torii.shmdn.link/>`_ platform definition for Squishy rev1 hardware.
If you are for some reason using Squishy rev1 as a general-purpose FPGA development board with Torii,
this is the platform you need to invoke.

Important
-------
This platform is for specialized hardware, as such it can not be used with any other hardware
than it was designed for. This includes any popular FPGA development or evaluation boards.

Note
----
There are no official releases of the Squishy rev1 hardware for purchase, and building one
is not recommended due to the current hardware errata for the platform.

'''

import logging                           as log
from argparse                            import Namespace
from pathlib                             import Path

from torii                               import *
from torii.build                         import *
from torii.build.run                     import BuildProducts
from torii.platform.vendor.lattice.ice40 import ICE40Platform
from torii.platform.resources.memory     import SPIFlashResources
from torii.platform.resources.user       import LEDResources
from torii.platform.resources.interface  import UARTResource

from .                                   import SquishyPlatform
from ...core.flash                       import Geometry as FlashGeometry
from ...core.config                      import FlashConfig, ICE40PLLConfig

__all__ = (
	'SquishyRev1',
)


class Rev1ClockDomainGenerator(Elaboratable):
	'''
	Clock domain and PLL generator for Squishy rev1.

	This module sets up two clock domains, ``usb`` and ``sync``. The ``usb``
	domain a 60MHz clock domain, and is fed from an external ULPI phy, where
	as the ``sync`` domain is the primary core clock domain and set for 100MHz
	and is fed from the global system input clock.

	Attributes
	----------
	pll_locked : Signal
		An active high signal indicating if the PLL is locked and stable.

	'''

	def __init__(self) -> None:
		self.pll_locked = Signal()

	def elaborate(self, platform: 'SquishyRev1') -> Module:
		m = Module()

		# The clock domains we want to have
		m.domains.usb  = ClockDomain()
		m.domains.sync = ClockDomain()

		# Set the clock to no-longer be a global so we can latch onto  it.
		platform.lookup(platform.default_clk).attrs['GLOBAL'] = False

		# Pull out the  PLL config and define the new PLL clock signal
		pll_cfg: ICE40PLLConfig = platform.pll_cfg
		pll_sync_clk = Signal()

		# Set up the PLL
		m.submodules.pll = Instance(
			'SB_PLL40_PAD',
			i_PACKAGEPIN = platform.request(platform.default_clk, dir = 'i'),
			i_RESETB     = Const(1),
			i_BYPASS     = Const(0),

			o_PLLOUTGLOBAL = pll_sync_clk,
			o_LOCK         = self.pll_locked,

			p_FEEDBACK_PATH = 'SIMPLE',

			p_DIVR         = pll_cfg.divr,
			p_DIVF         = pll_cfg.divf,
			p_DIVQ         = pll_cfg.divq,
			p_FILTER_RANGE = pll_cfg.filter_range,
		)

		# Add a clocking constraint for the new PLL core clock
		platform.add_clock_constraint(pll_sync_clk, pll_cfg.ofreq * 1e6)

		# Make sure we wiggle the domain on the clock
		m.d.comb += [
			# Hold domain in reset until the PLL stabilizes
			ResetSignal('sync').eq(~self.pll_locked),

			# Wiggle the clock
			ClockSignal('sync').eq(pll_sync_clk),
		]

		return m


class SquishyRev1(SquishyPlatform, ICE40Platform):
	'''
	Squishy hardware, Revision 1.

	This `Torii <https://torii.shmdn.link/>`_ platform is for the first revision of the Squishy SCSI hardware. It
	is based on the `Lattice iCE40-HX8K <https://www.latticesemi.com/iCE40>`_ and was primarily built to target SCSI-1 HVD
	only.

	The hardware `design files <https://github.com/squishy-scsi/hardware/tree/main/release/rev1>`_ can be found
	in the hardware repository on `GitHub <https://github.com/squishy-scsi/hardware>`_ under the ``release/rev1`` tree.

	'''

	device           = 'iCE40HX8K'
	package          = 'BG121'
	default_clk      = 'clk'
	toolchain        = 'IceStorm'
	bitstream_suffix = 'bin'

	revision     = (1, 0)

	flash = FlashConfig(
		geometry = FlashGeometry(
			size       = 8388608, # 8MiB
			page_size  = 256,
			erase_size = 4096,    # 4KiB
			slot_size  = 262144,  # 256KiB
			addr_width = 24
		),
		commands = {
			'erase': 0x20,
		}
	)

	pll_cfg = ICE40PLLConfig(
		divr         = 2,
		divf         = 34,
		divq         = 3,
		filter_range = 1,
		ofreq        = 70
	)

	clk_domain_generator = Rev1ClockDomainGenerator

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

		# TODO(aki): This needs to be re-thought out
		# SCSIPhyResource(0,
		# 	ack = ('C11', 'B11'), atn = ('H11', 'H10'), bsy = ('E11', 'E10'),
		# 	cd  = ('B5',  'A4' ), io  = ('B3',  'A2' ), msg = ('A8',  'B9' ),
		# 	sel = ('B7',  'A6' ), req = ('B4',  'A3' ), rst = ('E9',  'D9' ),
		# 	d0  = ('J11 G11 F11 D11 A10 C8 C9 B8', 'J10 G10 F10 D10 A11 C7 A9 A7'),
		# 	dp0 = ('B6',  'A5' ),
		#
		# 	tp_en  = 'A1', tx_en  = 'K11', aa_en = 'G8',
		# 	bsy_en = 'G9', sel_en = 'F9',  mr_en = 'E8',
		#
		# 	diff_sense = 'D7',
		#
		# 	attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		# ),

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

	def __init__(self) -> None:
		# Force us to always use the FOSS toolchain
		super().__init__(toolchain = 'IceStorm')

	def pack_artifact(self,  artifact: bytes, *, args: Namespace) -> bytes:
		'''
		Pack bitstream/gateware into device artifact.

		On Squishy rev1 platforms, there is no additional processing needed
		so this is effectively a no-op.

		Parameters
		----------
		artifact : bytes
			The input data of the result of gateware elaboration, typically
			the raw FPGA bitstream file.

		args: Namespace
			Command line arguments used when building the artifact.

		Returns
		-------
		bytes
			The input bytes from ``artifact``

		'''

		return artifact


	def _build_slots(self, geometry: FlashGeometry) -> bytes:
		'''
		Construct an iCE40 multi-boot viable flash image based on the platform flash topology.

		Parameters
		----------
		geometry : FlashGeometry
			The target device flash geometry

		Returns
		-------
		bytes
			The resulting slot data.
		'''

		from ...core.bitstream import iCE40BitstreamSlots

		slot_data = bytearray(geometry.erase_size)
		slots     = iCE40BitstreamSlots(geometry).build()

		# Replace the slot data as appropriate
		slot_data[0:len(slots)] = slots
		# Pad the remaining
		slot_data[len(slots):] = (0xFF for _ in range(geometry.erase_size - len(slots)))

		return bytes(slot_data)

	def build_image(self, name: str, build_dir: Path, boot_name: str, products: BuildProducts, *, args: Namespace) -> Path:
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

		args: Namespace
			Command line arguments used when building the image.

		Returns
		-------
		Path
			The path to the resulting image file.
		'''

		build_path = (build_dir / name)

		log.debug(f'Building multi-boot flash image in \'{build_path}\'')

		# Construct the bootloader asset name
		asset_name = boot_name
		if not asset_name.endswith('.bin'):
			asset_name += '.bin'

		with build_path.open('wb') as image:
			slot_data = self._build_slots(self.flash.geometry)

			log.debug(f'Writing {len(slot_data)} bytes of slot data')
			image.write(slot_data)

			log.debug(f'Writing bootloader \'{boot_name}\'')
			image.write(products.get(asset_name, 'b'))

			# Pad the result so we hit full slot density
			start = image.tell()
			end   = self.flash.geometry.partitions[1].start_addr

			pad_size = end - start

			log.debug(f'Padding bitstream with \'{pad_size}\' bytes')
			for _ in range(pad_size):
				image.write(b'\xFF')

			# Copy the bootloader entry pointer to the active slot
			image.write(slot_data[32:64])

		return build_path
