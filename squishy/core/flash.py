# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum import IntEnum, IntFlag

from construct import (
	Struct, Int8ul, Int32ul, Int24ul, Array, Byte, len_, this, Enum, FlagsEnum, Padding, Rebuild
)

__all__ = (
	'FPGAID',
	'SlotFlags',
	'rev2_flash_slot',
	'rev2_flash_layout',

	'Geometry',
	'Partition',
)

class FPGAID(IntEnum):
	LEF5UM25   = 0x01111043
	LEF5UM45   = 0x01112043
	LEF5UM85   = 0x01113043

	LEF5UM5G25 = 0x81111043
	LEF5UM5G45 = 0x81112043
	LEF5UM5G85 = 0x81113043

	BAD        = 0xFFFFFFFF

	@staticmethod
	def from_dev(name: str) -> 'FPGAID':
		match name[-6:]:
			case 'UM-25F':
				return FPGAID.LEF5UM25
			case 'UM-45F':
				return FPGAID.LEF5UM45
			case 'UM-85F':
				return FPGAID.LEF5UM85
			case '5G-25F':
				return FPGAID.LEF5UM5G25
			case '5G-45F':
				return FPGAID.LEF5UM5G45
			case '5G-85F':
				return FPGAID.LEF5UM5G85
			case _:
				return FPGAID.BAD

fpga_id = 'FPGA ID' / Enum(Int32ul, FPGAID)

class SlotFlags(IntFlag):
	F1 = 0b0000_0001
	F2 = 0b0000_0010
	F3 = 0b0000_0100
	F4 = 0b0000_1000
	F5 = 0b0001_0000
	F6 = 0b0010_0000
	F7 = 0b0100_0000
	F8 = 0b1000_0000

rev2_slot_flags = 'Slot Flags' / FlagsEnum(Int8ul, SlotFlags)

# Rev2+ Flash structure
rev2_slot_header = Struct(
	'fpga_id'          / fpga_id,
	'flags'            / rev2_slot_flags,
	'bitstream_length' / Rebuild(Int24ul, len_(this._.bitstream))
)

rev2_flash_slot = Struct(
	'header'    / rev2_slot_header,
	'bitstream' / Byte[this.header.bitstream_length],
)

rev2_flash_layout = Struct(
	'slots' / Array(3, Struct(
		'slot' / rev2_flash_slot,
		Padding(2097152 - len_(this.slot), pattern = b'\xFF')
	)),
	'data'  / Padding(2097152, pattern = b'\xFF')
)

class Partition:
	'''
	SPI Flash slot partition metadata.

	Parameters
	----------
	start_addr : int
		The start address of this partition.

	end_addr : int
		The end address of this partition.

	Attributes
	----------
	start_addr : int
		The start address of this partition.

	end_addr : int
		The end address of this partition.

	size : int
		The size in bytes of this partition.
	'''

	def __init__(self, *, start_addr: int, end_addr: int) -> None:
		self.start_addr = start_addr
		self.end_addr   = end_addr

	@property
	def size(self) -> int:
		return self.end_addr - self.start_addr

class Geometry:
	'''
	SPI Flash Geometry

	This class represents the geometry of the attached SPI flash, such as it's size,
	address with.

	It also provides a mechanism to segment the flash into slots for multi-boot/multi-image
	situations.

	Parameters
	----------
	size : int
		The total size in bytes of the flash.

	page_size : int
		The size in bytes of each flash page.

	erase_size : int
		The size in bytes of the effected area for the `erase` command.

	slot_size : int
		The size in bytes of any possible slots in this flash.

	slot_size : int
		The number of slots to place in flash. (default: 4)

	addr_width : int
		The size in bits of addresses for the flash. (default: 24)

	Attributes
	----------
	size : int
		The total size in bytes of the flash.

	page_size : int
		The size in bytes of each flash page.

	erase_size : int
		The size in bytes of the effected area for the `erase` command.

	slot_size : int
		The size in bytes of any possible slots in this flash.

	addr_width : int
		The size in bits of addresses for the flash.

	max_slots : int
		The maximum number of possible slots for this flash.

	slots : int
		The number of possible slots for this flash.

	partitions : dict[int, squishy.core.flash.Partition]
		The flash partition layout and slot mapping.

	'''

	def __init__(self, *, size: int, page_size: int, erase_size: int, slot_size: int, slot_count: int = 4, addr_width: int = 24) -> None:
		self.size       = size
		self.page_size  = page_size
		self.erase_size = erase_size
		self.slot_size  = slot_size
		self.addr_width = addr_width
		self._slots     = slot_count

	@property
	def max_slots(self) -> int:
		return self.size // self.slot_size

	@property
	def slots(self) -> int:
		slot_count = min(self._slots, self.max_slots)
		return slot_count

	@slots.setter
	def slots(self, slots: int) -> None:
		if slots > 2:
			raise ValueError(f'Must have at least 2 slots configured, {slots} specified')

		self._slots = slots

	@property
	def partitions(self) -> dict[int, Partition]:
		partitions: dict[int, Partition] = {}

		start_addr = self.erase_size

		for slot in range(self.slots):
			end_addr = self.slot_size if slot == 0 else start_addr + self.slot_size

			partitions[slot] = Partition(
				start_addr = start_addr,
				end_addr   = end_addr
			)

			if slot == 0:
				start_addr = self.slot_size
			else:
				start_addr += self.slot_size

		return partitions
