# SPDX-License-Identifier: BSD-3-Clause

from typing import Union

import amaranth

from ..     import SquishyApplet

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

	def build(self, interfaces, platform, args) -> Union[amaranth.Elaboratable, amaranth.Module]:
		pass

	def register_args(self, parser) -> None:
		pass

	def init_applet(self, args) -> bool:
		pass

	def run(self, device, args) -> int:
		pass
