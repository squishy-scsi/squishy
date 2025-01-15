/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_FPGA_HH)
#define SQUISHY_SUPERVISOR_FPGA_HH

#include <cstdint>

namespace squishy {
	namespace slots {
		constexpr inline std::uint8_t BOOTLOADER{0U};
		constexpr inline std::uint8_t APPLET1{1U};
		constexpr inline std::uint8_t APPLET2{2U};
		constexpr inline std::uint8_t REV2_EPHEMERAL{3U};
	}
	namespace registers {
		constexpr inline std::uint8_t CTRL{0U};
		constexpr inline std::uint8_t SLOT{1U};
		constexpr inline std::uint8_t TXLEN_HIGH{2U};
		constexpr inline std::uint8_t TXLEN_MID{3U};
		constexpr inline std::uint8_t TXLEN_LOW{4U};
		constexpr inline std::uint8_t IRQ{5U};

		constexpr inline std::uint8_t CTRL_WRITE_DONE{1U << 0U};
		constexpr inline std::uint8_t CTRL_IRQ_ACK{1U << 1U};

		constexpr inline std::uint8_t SLOT_BOOT_MASK{0x0FU};
		constexpr inline std::uint8_t SLOT_DEST_MASK{0xF0U};

		constexpr inline std::uint8_t IRQ_WANT_DFU{1U << 0U};
		constexpr inline std::uint8_t IRQ_WRITE_SLOT{1U << 1U};
		constexpr inline std::uint8_t IRQ_BOOT{1U << 2U};
	}
}


void setup_fpga_ctrl_pins() noexcept;
void fpga_enter_cfg() noexcept;
[[nodiscard]]
bool fpga_handle_irq() noexcept;

#endif /* SQUISHY_SUPERVISOR_FPGA_HH */
