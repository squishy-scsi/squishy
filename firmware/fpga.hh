/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_FPGA_HH)
#define SQUISHY_SUPERVISOR_FPGA_HH

#include <cstdint>

namespace squishy::registers {
	constexpr inline std::uint8_t CTRL{0U};
	constexpr inline std::uint8_t SLOT{1U};
	constexpr inline std::uint8_t TXLEN_HIGH{2U};
	constexpr inline std::uint8_t TXLEN_LOW{3U};
	constexpr inline std::uint8_t IRQ{4U};
}

void setup_fpga_ctrl_pins() noexcept;
void fpga_enter_cfg() noexcept;

#endif /* SQUISHY_SUPERVISOR_FPGA_HH */
