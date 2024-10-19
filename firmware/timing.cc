/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>
#include <atomic>

#include "peripherals.hh"
#include "units.hh"

#include "timing.hh"

std::atomic<std::uint32_t> ms_elapsed{0U};


void delay(const std::uint32_t ms_delay) noexcept {
	const timeout_t timeout{ms_delay};
	timeout.wait();
}

timeout_t::timeout_t(const std::uint32_t timeout_value) noexcept {
	_expiry_time = ms_elapsed + timeout_value;
}

[[nodiscard]]
bool timeout_t::has_expired() const noexcept {
	const auto count{ms_elapsed.load()};

	// Check for the tricky overflow condition and handle that properly -
    // when ms_elapsed approaches UINT32_MAX and we try to set a timeout that
    // overflows to a low _expiry_time value, if we simply compare with `>`, we will
    // erroneously consider the timeout expired for a few ms right at the start of
    // the valid interval. Instead, force that region of time to be considered
    // not expired by checking the MSb's of the two values and handling that specially.
    if ((count & UINT32_C(0x80000000)) && !(_expiry_time & UINT32_C(0x80000000))) {
      return false;
	}
    // For normal combinations of counter and expiry time, compare normally
    return count > _expiry_time;
}

void timeout_t::wait() const noexcept {
	while (!has_expired()) {
		asm ("wfi");
	}
}
