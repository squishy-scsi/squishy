# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from abc              import ABCMeta, abstractmethod
from argparse         import Namespace
from pathlib          import Path
from typing           import TypeAlias
from itertools        import count

from torii.hdl        import Elaboratable
from torii.build      import Resource, ResourceError
from torii.build.plat import Platform
from torii.build.run  import BuildProducts

from ...core.config   import PLLConfig, FlashConfig

__all__ = (
	'SquishyPlatform',
	'SquishyPlatformType',
)

class SquishyPlatform(metaclass = ABCMeta):
	'''
	Base Squishy Hardware platform

	This represents all the common properties and methods
	that all Squishy hardware platforms are required to have.

	This also implements the applet bitstream cache mechanisms.

	Attributes
	----------

	revision : tuple[int, int]
		The revision of the hardware this platform supports, in the form
		of (major, minor).

	revision_str : str
		The canonicalize revision as a string in the form of 'major.minor'.

	bitstream_suffix : str
		The suffix of the FPGA bitstream that is generated when gateware is built for this platform.

	flash : FlashConfig
		The configuration of the attached SPI boot flash.

	pll_cfg : PLLConfig
		The PLL configuration that is passed to the ``clk_domain_generator`` of this platform
		when instantiated.

	clk_domain_generator : type[torii.Elaboratable]
		The type of clock domain generator for this platform. It is instantiated and hooked up
		to the gateware on elaboration.

	ephemeral_slot : int | None
		If this platform supports ephemeral applet flashing, then this is the DFU alt-mode to use, otherwise None

	Important
	---------
	Platforms are also still required to inherit from the appropriate :py:mod:`torii.vendor.platform`
	in order to properly be used.

	'''

	@property
	@abstractmethod
	def revision(self) -> tuple[int, int]:
		''' The hardware revision of this platform in the form of (major, minor) '''
		raise NotImplementedError('SquishyPlatform requires a revision to be set')

	@property
	def revision_str(self) -> str:
		''' The canonicalize revision as a string in the form of 'major.minor' '''
		return '.'.join(map(lambda p: str(p), self.revision))

	@property
	@abstractmethod
	def bitstream_suffix(self) -> str:
		''' The suffix of the FPGA bitstream that is generated when gateware is built for this platform '''
		raise NotImplementedError('SquishyPlatform requires a revision to be set')

	@property
	@abstractmethod
	def flash(self) -> FlashConfig:
		''' The attached SPI boot flash configuration '''
		raise NotImplementedError('SquishyPlatform requires a flash config to be set')

	@property
	@abstractmethod
	def pll_cfg(self) -> PLLConfig:
		''' PLL Configuration for the platforms clock domain generator '''
		raise NotImplementedError('SquishyPlatform requires a PLL config to be set')

	@property
	@abstractmethod
	def clk_domain_generator(self) -> type[Elaboratable]:
		''' The Torii Elaboratable used to setup the PLL and clock domains for the platform '''
		raise NotImplementedError('SquishyPlatform requires a PLL config to be set')

	@property
	def ephemeral_slot(self) -> int | None:
		''' If this platform supports ephemeral applet flashing, then this is the DFU alt-mode to use '''
		return None

	# TODO(aki): single bitstream/artifact packing + whole image packing
	@abstractmethod
	def pack_artifact(self, artifact: bytes, *, args: Namespace) -> bytes:
		'''
		Pack a signal bitstream image into a device appropriate artifact.

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
			The result of the artifact packing process

		'''
		raise NotImplementedError('SquishyPlatform requires pack_artifact to be implemented')

	@abstractmethod
	def build_image(self, name: str, build_dir: Path, boot_name: str, products: BuildProducts, *, args: Namespace) -> Path:
		'''
		Build a platform compatible flash image for provisioning.

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
		raise NotImplementedError('SquishyPlatform requires build_image to be implemented')

	def all_resources_by_name(self, name: str) -> list[Resource]:
		'''
		Get all resources sharing a common root name, e.g. all LEDs

		Parameters
		----------
		name : str
			The base name of the resources to collect.

		Returns
		-------
		list[Resources]
			A list of all of the found Torii resources matching the given base name.

		'''

		res = []
		for num in count():
			try:
				res.append(self.request(name, num))
			except ResourceError:
				break
		return res

# XXX(aki): This is a stupid hack so we get proper typing on the platform
#           without the nightmare that is recursive imports and all that jazz.
#           I would really *really* love to do a proper composite type class but
#           a union works for now.
SquishyPlatformType: TypeAlias = SquishyPlatform | Platform
