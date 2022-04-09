# SPDX-License-Identifier: BSD-3-Clause

from .. import SquishyApplet

class Analyzer(SquishyApplet):
	preview      = True
	pretty_name  = 'SCSI Analyzer'
	description  = 'SCSI Bus analyzer and replay'
	short_help   = description
	hardware_rev = (
		'rev1', 'rev2'
	)

	def build(self, target, args):
		pass

	def register_args(self, parser):
		pass

	def init_applet(self, args):
		pass

	def run(self, device, args):
		pass
