# SPDX-License-Identifier: BSD-3-Clause

'''

The analyzer applet turns squishy into a passive SCSI bus sniffer, allowing for you to inspect, copy, replay,
and modify SCSI traffic.

It uses the :py:mod:`squishy.core.pcapng` module to write ```LINKTYPE_PARALLEL_SCSI```_ compatible `PCAPNG`_
files.


.. _LINKTYPE_PARALLEL_SCSI: https://github.com/squishy-scsi/wireshark-scsi/docs/LINKTYPE_PARALLEL_SCSI.md
.. _PCAPNG: https://datatracker.ietf.org/doc/draft-ietf-opsawg-pcapng/02/

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
