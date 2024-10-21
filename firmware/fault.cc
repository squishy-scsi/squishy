/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>
#include <atomic>
#include <array>

#include "fault.hh"
#include "peripherals.hh"
#include "pindefs.hh"

std::atomic<fault_code_t> active_fault{fault_code_t::NONE};

static std::uint16_t displayed_fault{};
static std::uint8_t bit_index{};
static std::uint8_t cycles_rem{};
static std::uint8_t curr_nybble{4U};

constexpr static std::array<std::uint8_t, 16> blink_table{{
/*   Bits'Pattern  Val  */
	0b101'11111, /* 0 (- - - - -) */
	0b101'11110, /* 1 (. - - - -) */
	0b101'11100, /* 2 (. . - - -) */
	0b101'11000, /* 3 (. . . - -) */
	0b101'10000, /* 4 (. . . . -) */
	0b101'00000, /* 5 (. . . . .) */
	0b101'00001, /* 6 (- . . . .) */
	0b101'00011, /* 7 (- - . . .) */
	0b101'00111, /* 8 (- - - . .) */
	0b101'01111, /* 9 (- - - - .) */
	0b010'00010, /* A (. -)       */
	0b100'00001, /* B (- . . .)   */
	0b100'00101, /* C (- . - .)   */
	0b011'00001, /* D (- . .)     */
	0b001'00000, /* E (.)         */
	0b100'00100, /* F (. . - .)   */
}};

void update_fault_led() noexcept {
	if (curr_nybble == 4U) {
		displayed_fault = static_cast<std::uint16_t>(active_fault.load());
		if (displayed_fault == 0U) {
			return;
		}

		curr_nybble = 0U;
		bit_index   = 0U;
	}

	if (cycles_rem == 0U) {
		const auto nybble{std::uint8_t((displayed_fault >> ((3U - curr_nybble) * 4U)) & 0xFU)};
		const auto blnk_pattern{blink_table[nybble]};
		const auto patrn_len{std::uint8_t((blnk_pattern & 0b111'00000) >> 5U)};

		if (bit_index == patrn_len) {
			cycles_rem = 3U;
			++bit_index;
			return;
		} else if (bit_index > patrn_len) {
			++curr_nybble;
			bit_index = 0U;
			return;
		}

		cycles_rem = (blnk_pattern & (1U << bit_index)) ? 3U : 1U;
		++bit_index;

		PORTA.set_low(pin::SU_LED_R);
	} else {
		if (cycles_rem == 1U) {
			PORTA.set_high(pin::SU_LED_R);
		}

		--cycles_rem;
	}

}
