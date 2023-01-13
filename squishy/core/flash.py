# SPDX-License-Identifier: BSD-3-Clause

from typing import (
	Dict
)

__doc__ = '''\

'''

__all__ = (
	'FlashGeometry',
)

class FlashGeometry:
	''' SPI Flash Geometry '''

	def __init__(self, *, size: int, page_size: int, erase_size: int, addr_width: int = 24) -> None:
		'''  '''

		self.size       = size
		self.page_size  = page_size
		self.erase_size = erase_size
		self.addr_width = addr_width

	@property
	def slots(self) -> int:
		possible_slots = self.size // self.slot_size
		slots = min(self._slots, possible_slots)
		assert slots > 1, f'{slots}'
		return slots

	@slots.setter
	def slots(self, slots: int):
		assert slots >= 2, f'Must have at least 2 flash slots configured, {slots} specified'
		self._slots = slots

	@property
	def partitions(self) -> Dict[int, Dict[str, int]]:

		partitions = dict()

		start_addr = self.erase_size

		for slot in range(self.slots):
			end_addr = self.slot_size if slot == 0 else start_addr + self.slot_size

			partitions[slot] = {
				'start_addr': start_addr,
				'end_addr': end_addr
			}

			if slot == 0:
				start_addr = self.slot_size
			else:
				start_addr += self.slot_size
		return partitions

	def init_slots(self, device: str) -> 'FlashGeometry':

		self.slots = 4

		self.slot_size = {
			'iCE40HX8K': 2**18,
			'LFE5UM5G-45F': 2**21,
		}.get(device, None)

		assert self.slot_size is not None, f'Unsupported platform device {device}'

		return self
