/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_UNITS_HH)
#define SQUISHY_SUPERVISOR_UNITS_HH

#include <cstdint>
#include <span>

[[nodiscard]]
constexpr std::uint32_t operator ""_KiB(const unsigned long long value) noexcept { return std::uint32_t(value) * 1'024; }
[[nodiscard]]
constexpr std::uint32_t operator ""_MiB(const unsigned long long value) noexcept { return std::uint32_t(value) * 1'048'576; }

[[nodiscard]]
constexpr std::uint32_t operator ""_kHz(const unsigned long long value) noexcept { return std::uint32_t(value) * 1'000; }
[[nodiscard]]
constexpr std::uint32_t operator ""_MHz(const unsigned long long value) noexcept { return std::uint32_t(value) * 1'000'000; }

/* Convert a span of 4 bytes into a little-endian uint32_t */
[[nodiscard]]
std::uint32_t read_le(const std::span<std::uint8_t, 4>& data) noexcept;

/* Convert a span of 4 bytes into a big-endian uint32_t */
[[nodiscard]]
std::uint32_t read_be(const std::span<std::uint8_t, 4>& data) noexcept;

#endif /* SQUISHY_SUPERVISOR_UNITS_HH */
