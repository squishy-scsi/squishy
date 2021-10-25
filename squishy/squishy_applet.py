# SPDX-License-Identifier: BSD-3-Clause
from abc import ABCMeta, abstractmethod

__all__ = (
	'SquishyApplet',
)

class SquishyApplet(metaclass = ABCMeta):
	help         = '<HELP MISSING>'
	description  = '<DESCRIPTION MISSING>'
	required_rev = 'rev1'

	@abstractmethod
	def synth(self, target):
		pass

	@abstractmethod
	def run(self, device, args):
		pass

