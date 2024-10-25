/* SPDX-License-Identifier: BSD-3-Clause */
#pragma once
#if !defined(SQUISHY_SUPERVISOR_SPI_HH)
#define SQUISHY_SUPERVISOR_SPI_HH

#include <cstdint>

#include <span>

[[nodiscard]]
bool setup_spi() noexcept;

void read_flash(std::uint32_t addr, std::span<std::uint8_t> buffer) noexcept;
void erase_flash(std::uint32_t addr, std::size_t length) noexcept;
void write_flash(std::uint32_t addr, const std::span<std::uint8_t>& buffer) noexcept;

void read_psram(std::uint32_t addr, std::span<std::uint8_t> buffer) noexcept;
void write_psram(std::uint32_t addr, const std::span<std::uint8_t>& buffer) noexcept;

/* Load the bitstream from the given slot into the FPGA */
[[nodiscard]]
bool load_bitstream_flash(std::uint8_t slot_index) noexcept;


#endif /* SQUISHY_SUPERVISOR_SPI_HH */
