/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_FAULT_HH)
#define SQUISHY_SUPERVISOR_FAULT_HH

#include <cstdint>
#include <atomic>

enum struct fault_code_t : std::uint16_t {
	None     = 0x0000U,


	SPI_FLASH_BAD     = 0x0001U,
	FPGA_ID_BAD       = 0x0002U,
	FPGA_ID_MISMATCH  = 0x0003U,
	FPGA_CFG_INVALID  = 0x0004U,
	SLOT_HEADER_BAD   = 0x0005U,
	SLOT_INDEX_BAD    = 0x0006U,
	FPGA_CFG_FAILED   = 0x0007U,
	FPGA_BIT_MISMATCH = 0x0008U,
};

extern std::atomic<fault_code_t> active_fault;

#endif /* SQUISHY_SUPERVISOR_FAULT_HH */