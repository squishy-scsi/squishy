# SPDX-License-Identifier: BSD-3-Clause

from torii       import Module

from ..          import SquishyApplet
from ...gateware import AppletElaboratable

class AnalyzerElaboratable(AppletElaboratable):

	def elaborate(self, platform) -> Module:
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
	supports_gui  = True
	supports_repl = True

	def init_gui(self, main_window, args) -> bool:
		pass

	def init_repl(self, repl_ctx, args) -> bool:
		pass

	def register_args(self, parser) -> None:
		pass

	def init_applet(self, args) -> AppletElaboratable:
		return AnalyzerElaboratable()

	def run(self, device, args) -> int:
		pass
