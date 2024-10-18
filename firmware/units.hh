/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_UNITS_HH)
#define SQUISHY_SUPERVISOR_UNITS_HH

#include <cstdint>

constexpr std::uint32_t operator ""_KiB(const unsigned long long value) noexcept { return std::uint32_t(value) * 1024; }
constexpr std::uint32_t operator ""_MiB(const unsigned long long value) noexcept { return std::uint32_t(value) * 1048576; }

#endif /* SQUISHY_SUPERVISOR_UNITS_HH */
