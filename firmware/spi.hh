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

[[nodiscard]]
std::uint32_t read_psram(std::uint32_t addr, std::span<std::uint8_t> buffer) noexcept;
[[nodiscard]]
std::uint32_t write_psram(std::uint32_t addr, const std::span<std::uint8_t>& buffer) noexcept;


/* Load the bitstream from the given slot into the FPGA */
[[nodiscard]]
bool load_bitstream_flash(std::uint8_t slot_index) noexcept;
/* Load bitstream from PSRAM into FPGA directly */
[[nodiscard]]
bool load_bitstream_psram() noexcept;
/* Shuffle the data from the PSRAM to FLASH, note that expected_len does not include the header size */
[[nodiscard]]
bool move_to_slot(std::uint8_t slot_index, std::uint32_t expected_len) noexcept;

[[nodiscard]]
std::uint8_t read_squishy_register(std::uint8_t addr) noexcept;
void write_squishy_register(std::uint8_t addr, std::uint8_t val) noexcept;

#endif /* SQUISHY_SUPERVISOR_SPI_HH */
