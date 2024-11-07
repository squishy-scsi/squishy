# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from torii          import Module
from argparse       import ArgumentParser, Namespace


from ..             import SquishyApplet
from ...gateware    import AppletElaboratable, SquishyPlatformType
from ...device      import SquishyDevice

__all__ = (
	'Analyzer',
)

class AnalyzerElaboratable(AppletElaboratable):
	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		return m

class Analyzer(SquishyApplet):
	'''

	'''

	name                = 'analyzer'
	description         = 'SCSI Bus analyzer and traffic replay'
	version             = 0.1
	preview             = True
	supported_platforms = (
		(1, 0),
		(2, 0)
	)

	def register_args(self, parser: ArgumentParser) -> None:
		pass

	def initialize(self, args: Namespace) -> AppletElaboratable:
		return AnalyzerElaboratable()

	def run(self, args: Namespace, dev: SquishyDevice) -> int:
		pass
