# SPDX-License-Identifier: BSD-3-Clause

'''
.. todo: Refine this section

The Squishy gateware library is broken into three main parts. The first is the
:py:mod:`squishy.gateware.core` module, this contains all of the core infra for
Squishy. Next is the :py:mod:`squishy.gateware.platform` module, this contains
the torii platform definitions for various bits of Squishy hardware.
Finally there is the :py:mod:`squishy.gateware.scsi` module, this is where all
of the SCSI machinery is for use in torii HDL projects.

'''

from torii          import Elaboratable, Module

from .applet        import AppletElaboratable
from .bootloader    import SquishyBootloader
from .platform      import SquishyPlatform, SquishyPlatformType
from .platform.rev1 import SquishyRev1
from .platform.rev2 import SquishyRev2

__all__ = (
	'SquishyPlatform',
	'SquishyPlatformType',

	'Squishy',
	'SquishyBootloader',
	# All viable Squishy platforms
	'AVAILABLE_PLATFORMS',
)

AVAILABLE_PLATFORMS: dict[str, type[SquishyPlatform]] = {
	'rev1': SquishyRev1,
	'rev2': SquishyRev2,
}


class Squishy(Elaboratable):
	'''
	Squishy applet gateware superstructure.


	Parameters
	----------
	revision : tuple[int, int]
		The target platforms revision.

	applet : AppletElaboratable
		The applet.

	'''

	def __init__(self, *, revision: tuple[int, int], applet: AppletElaboratable) -> None:
		self.applet        = applet
		self.plat_revision = revision

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		m.submodules.pll    = platform.clk_domain_generator()
		m.submodules.applet = self.applet

		return m
