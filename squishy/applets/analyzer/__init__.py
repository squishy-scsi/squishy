# SPDX-License-Identifier: BSD-3-Clause

from torii          import Module
from argparse       import ArgumentParser, Namespace


from ..             import SquishyApplet
from ...gateware    import AppletElaboratable, SquishyPlatform
from ...core.device import SquishyHardwareDevice


class AnalyzerElaboratable(AppletElaboratable):

	def elaborate(self, platform: SquishyPlatform | None) -> Module:
		m = Module()

		return m

class Analyzer(SquishyApplet):
	preview       = True
	pretty_name   = 'SCSI Analyzer'
	description   = 'SCSI Bus analyzer and replay'
	short_help    = description
	hardware_rev  = (
		'rev1', 'rev2'
	)

	def register_args(self, parser: ArgumentParser) -> None:
		pass

	def init_applet(self, args: Namespace) -> AppletElaboratable:
		return AnalyzerElaboratable()

	def run(self, device: SquishyHardwareDevice, args: Namespace) -> int:
		pass
