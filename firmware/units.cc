/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>
#include <span>

#include "units.hh"

/* Convert a span of 4 bytes into a little-endian uint32_t */
[[nodiscard]]
std::uint32_t read_le(const std::span<std::uint8_t, 4>& data) noexcept {
	return
		(std::uint32_t(data[3]) << 24U) |
		(std::uint32_t(data[2]) << 16U) |
		(std::uint32_t(data[1]) <<  8U) |
		std::uint32_t(data[0])
	;
}

/* Convert a span of 4 bytes into a big-endian uint32_t */
[[nodiscard]]
std::uint32_t read_be(const std::span<std::uint8_t, 4>& data) noexcept {
	return
		(std::uint32_t(data[0]) << 24U) |
		(std::uint32_t(data[1]) << 16U) |
		(std::uint32_t(data[2]) <<  8U) |
		std::uint32_t(data[3])
	;
}
