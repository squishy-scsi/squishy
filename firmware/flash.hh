/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_FLASH_HH)
#define SQUISHY_SUPERVISOR_FLASH_HH

#include <cstdint>
#include <array>
#include <limits>

#include "units.hh"

/*
	╭────────╮ 0x00000000
	│ SLOT 0 ├─────────────────╮
	├────────┤ 0x00200000 ╭────┴────╮ 0x00N00000
	│ SLOT 1 │            │ SLT HDR ├─────────────────╮
	├────────┤ 0x00400000 ├─────────┤ 0x00N00008 ╭────┴────╮ 0x00N00000
	│ SLOT 2 │            │ SLT DAT │            │ FPGA ID │
	├────────┤ 0x00600000 ╰─────────╯ 0x00NFFFFF ├─────────┤ 0x00N00004
	│ META 0 ├─────────────────╮                 │  FLAGS  │
	╰────────╯ 0x00800000 ╭────┴────╮ 0x00600000 ├─────────┤ 0x00N00005
                          │  RSRVD  │            │ BIT LEN │
						  ╰─────────╯ 0x00800000 ╰─────────╯ 0x00N00008

	Slot Allocation:
		Slot 0: Bootloader
		Slot 1: applet gateware
		Slot 2: Unallocated
*/

enum struct fpga_id_t : std::uint32_t {
	LEF5UM25   = 0x01111043U,
	LEF5UM45   = 0x01112043U,
	LEF5UM85   = 0x01113043U,

	LEF5UM5G25 = 0x81111043U,
	LEF5UM5G45 = 0x81112043U,
	LEF5UM5G85 = 0x81113043U,

	BAD = std::numeric_limits<std::uint32_t>::max(),
};

enum struct flash_flags_t : std::uint8_t {
	F1 = 0b0000'0001,
	F2 = 0b0000'0010,
};

struct slot_header_t final {
	fpga_id_t idcode;
	flash_flags_t flags;
	std::array<std::uint8_t, 3> len;

	std::uint32_t bitstream_len() const noexcept {
		return
			(std::uint32_t(len[2]) << 16U) |
			(std::uint32_t(len[1]) <<  8U) |
			std::uint32_t(len[0])
		;
	}
};

struct flash_slot_t final {
	slot_header_t header;
	std::array<std::uint8_t, 2_MiB - sizeof(slot_header_t)> data;
};

struct flash_layout_t final {
	std::array<flash_slot_t, 3> bitstreams;
	std::array<std::uint8_t, 2_MiB> data;
};

#endif /* SQUISHY_SUPERVISOR_FLASH_HH */
