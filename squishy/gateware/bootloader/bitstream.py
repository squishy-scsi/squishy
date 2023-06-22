# SPDX-License-Identifier: BSD-3-Clause

import logging      as log
from enum           import IntEnum, IntFlag, unique


from construct      import (
	this,
	Switch, StopIf, Rebuild, Padded, GreedyRange,
	Struct, BitStruct, Enum, FlagsEnum,
	Bytewise, Const,
	Nibble, Int8ub, Int16ub, Int24ub, Int32ub
)

from ...core.flash  import FlashGeometry

__doc__ = '''\

'''

__all__ = (
	'iCE40BitstreamSlots',
)

class iCE40BitstreamSlots:

	@unique
	class Opcodes(IntEnum):
		SPECIAL       = 0
		BANK_NUM      = 1
		CRC_CHECK     = 2
		BOOT_ADDR     = 4
		INT_OSC_RANGE = 5
		BANK_WIDTH    = 6
		BANK_HEIGHT   = 7
		BANK_OFFSET   = 8
		BOOT_MODE     = 9

	@unique
	class SpecialOpcode(IntEnum):
		CRAM_DATA = 1
		BRAM_DATA = 3
		RESET_CRC = 5
		WAKEUP    = 6
		REBOOT    = 8

	@unique
	class BootModes(IntFlag):
		SIMPLE = 0
		COLD   = 16
		WARM   = 32

	_special = Struct(
		'op' / Enum(Int8ub, SpecialOpcode),
	)

	_bootmode = Struct(
		'reserved' / Const(0, Int8ub),
		'mode'     / FlagsEnum(Int8ub, BootModes),
	)

	_bankoffset = Struct(
		'offset' / Int16ub,
	)

	_bootaddr = Struct(
		'addr_len' / Const(3, Int8ub),
		'addr'     / Int24ub,
	)

	_payload = Switch(
		this.instruction, {
			Opcodes.SPECIAL    : _special,
			Opcodes.BOOT_ADDR  : _bootaddr,
			Opcodes.BANK_OFFSET: _bankoffset,
			Opcodes.BOOT_MODE  : _bootmode,
		}
	)

	_instruction = BitStruct(
		'instruction' / Enum(Nibble, Opcodes),
		StopIf(this.instruction == 0xF),
		'byte_count' / Rebuild(Nibble, lambda this:
			this._subcons.payload.sizeof(**this) // 8
		),
		'payload' / Bytewise(_payload),
	)

	_slot = Struct(
		'magic' / Const(0x7EAA997E, Int32ub),
		'bitstream' / Padded(28,
			GreedyRange(_instruction),
			pattern = b'\xFF'
		)
	)

	def __init__(self, flash_geometry: FlashGeometry) -> None:
		self._geometry = flash_geometry

	def build(self) -> bytearray:

		data = bytearray(32 * 5)

		log.info(f'Serializing {len(data)} bytes for slot data')

		slots = self._build_slots(self._geometry)

		log.debug('Copying boot slot')
		data[0:32] = slots[1]

		slot_offset = 32
		for slot in slots:
			assert len(slot) == 32
			log.debug(f'Copying slot {slot}')
			data[slot_offset:slot_offset + 32] = slot
			slot_offset += 32

		log.debug('Filling remaining')
		slot = slots[-1]
		for _ in range(len(slots), 4):
			data[slot_offset:slot_offset + 32] = slot
			slot_offset += 32

		return data

	@staticmethod
	def _build_slots(flash_geometry: FlashGeometry) -> list[bytes]:

		partitions = flash_geometry.partitions
		slots = []

		for slot in range(flash_geometry.slots):
			slots.append(iCE40BitstreamSlots._build_slot(partitions[slot]))

		return slots


	@staticmethod
	def _build_slot(partition : dict[str, int]) -> bytes:
		return iCE40BitstreamSlots._slot.build({
			'bitstream': [
				{
					'instruction': iCE40BitstreamSlots.Opcodes.BOOT_MODE,
					'payload': { 'mode': iCE40BitstreamSlots.BootModes.SIMPLE }
				},
				{
					'instruction': iCE40BitstreamSlots.Opcodes.BOOT_ADDR,
					'payload': { 'addr': partition['start_addr'] }
				},
				{
					'instruction': iCE40BitstreamSlots.Opcodes.BANK_OFFSET,
					'payload': { 'offset': 0, }
				},
				{
					'instruction': iCE40BitstreamSlots.Opcodes.SPECIAL,
					'payload': { 'op': iCE40BitstreamSlots.SpecialOpcode.REBOOT }
				}
			]
		})
