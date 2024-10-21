/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_FAULT_HH)
#define SQUISHY_SUPERVISOR_FAULT_HH

#include <cstdint>
#include <atomic>

enum struct fault_code_t : std::uint16_t {
	NONE              = 0x0000U,

	SPI_FLASH_BAD     = 0x0001U,

	SLOT_HEADER_BAD   = 0x0002U,
	SLOT_INDEX_BAD    = 0x0003U,

	FPGA_ID_BAD       = 0x0004U,
	FPGA_ID_MISMATCH  = 0x0005U,
	FPGA_CFG_INVALID  = 0x0006U,
	FPGA_CFG_FAILED   = 0x0007U,
	FPGA_BIT_MISMATCH = 0x0008U,

	SPI_PSRAM_BAD     = 0x0009U,

};

extern std::atomic<fault_code_t> active_fault;

void update_fault_led() noexcept;

#endif /* SQUISHY_SUPERVISOR_FAULT_HH */
