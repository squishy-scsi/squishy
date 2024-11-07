# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from construct import Struct, Int8ul, Int32ul, Int24ul, Array, len_, this

__all__ = (
	'Geometry',
	'Partition',
)


# Rev2+ Flash structure
slot_header = Struct(
	'fpga_id'          / Int32ul,
	'flags'            / Int8ul,
	'bitstream_length' / Int24ul
)

flash_slot = Struct(
	'header'    / slot_header,
	'bitstream' / Array(len_(this.header) - 2097152, Int8ul)
)

flash_layout = Struct(
	'slots' / Array(3, flash_slot),
	'data'  / Array(2097152, Int8ul)
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
