/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_PINDEFS_HH)
#define SQUISHY_SUPERVISOR_PINDEFS_HH

#include <cstdint>

namespace pin {
	/* 32MHz input clock */
	inline constexpr std::uint8_t CLKIN{8U};

	/* Supervisor Status LEDS */
	inline constexpr std::uint8_t SU_LED_G{2U};
	inline constexpr std::uint8_t SU_LED_R{3U};

	/* User-facing DFU trigger */
	inline constexpr std::uint8_t DFU_BTN{9U}; // EXTINT7

	/* Bitstream/configuration flash storage */
	inline constexpr std::uint8_t FLASH_CS{4U};
	inline constexpr std::uint8_t FLASH_CLK{5U};
	inline constexpr std::uint8_t FLASH_COPI{6U};
	inline constexpr std::uint8_t FLASH_CIPO{7U};

	/* External PSRAM on the FPGA SPI Bus  */
	inline constexpr std::uint8_t PSRAM_CS{14U};

	/* FPGA SPI Comm/Programming bus */
	/* BUG: The schematic and PCB layout are out of sync for these, go with the PCB layout */
	inline constexpr std::uint8_t FPGA_CS{22U};
	inline constexpr std::uint8_t FPGA_COPI{16U};
	inline constexpr std::uint8_t FPGA_CIPO{17U};
	inline constexpr std::uint8_t FPGA_CLK{23U};

	/* FPGA Configuration interface signals */
	inline constexpr std::uint8_t FPGA_HOLD{10U};
	inline constexpr std::uint8_t FPGA_INIT{24U};
	inline constexpr std::uint8_t FPGA_PROG{25U};
	inline constexpr std::uint8_t FPGA_DONE{27U};

	/* FPGA Facing DFU/Comm triggers */
	inline constexpr std::uint8_t SU_ATTN{15U}; // This EXTINT1 needs to be rising edge, not level
	inline constexpr std::uint8_t BUS_HOLD{11U};
}

#endif /* SQUISHY_SUPERVISOR_PINDEFS_HH */
