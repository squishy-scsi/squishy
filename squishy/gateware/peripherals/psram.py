# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum           import IntEnum, auto, unique

from ..platform     import SquishyPlatformType
from torii          import Elaboratable, Module, Signal
from torii.lib.fifo import AsyncFIFO


@unique
class SPIPSRAMCmd(IntEnum):
	''' SPI PSRAM Command Opcodes '''
	READ          = 0x03
	WRITE         = 0x02
	FAST_READ     = 0x0B
	RESET_ENABLE  = 0x66
	RESET         = 0x99
	READ_ID       = 0x9F
	SET_BURST_LEN = 0xC0

class SPIPSRAM(Elaboratable):
	'''

	This module primarily implements the SPI interface for the ISSI ``IS66WVS2M8ALL/BLL``/``IS67WVS2M8ALL/BLL``
	SPI PSRAM. The datasheet can be found `here <https://www.issi.com/WW/pdf/66-67WVS2M8ALL-BLL.pdf>`_.



	'''

	def __init__(self) -> None:
		pass

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()



		return m
