# SPDX-License-Identifier: BSD-3-Clause

from typing import Any

from torii  import Elaboratable, Module


__doc__ = '''\

'''

__all__ = (
	'Rev2USB',
)


class Rev2USB(Elaboratable):
	def __init__(self, *, config: dict[str, Any]) -> None:
		self.config = config

	def elaborate(self, platform) -> Module:
		m = Module()


		return m
