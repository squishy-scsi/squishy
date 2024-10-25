/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_MEMORY_HH)
#define SQUISHY_SUPERVISOR_MEMORY_HH

#include <cstddef>
#include <cstdint>

extern "C" void* memcpy(void* dest, const void* src, const std::size_t size) noexcept;
extern "C" void* memset(void* dest, const std::uint8_t val, const std::size_t size) noexcept;
extern "C" void* memcmp(const void* lhs, const void* rhs, const std::size_t size) noexcept;

#endif /* SQUISHY_SUPERVISOR_MEMORY_HH */
