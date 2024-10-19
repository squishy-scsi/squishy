/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_TIMING_HH)
#define SQUISHY_SUPERVISOR_TIMING_HH

#include <cstdint>
#include <atomic>

extern std::atomic<std::uint32_t> ms_elapsed;

void delay(const std::uint32_t ms_delay) noexcept;

struct timeout_t final {
private:
	std::uint32_t _expiry_time;
public:
	timeout_t(std::uint32_t timeout_value) noexcept;

	[[nodiscard]]
	bool has_expired() const noexcept;

	void wait() const noexcept;
};


#endif /* SQUISHY_SUPERVISOR_TIMING_HH */
