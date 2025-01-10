/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>

#include "spi.hh"

#include "peripherals.hh"
#include "pindefs.hh"
#include "units.hh"
#include "timing.hh"
#include "flash.hh"
#include "fault.hh"
#include "fpga.hh"
#include "memory.hh"

enum struct flash_cmd_t : std::uint16_t {
	WRITE_ENABLE  = 0x0006U,
	WRITE_DISABLE = 0x0004U,
	READ_STATUS   = 0x0005U,
	READ          = 0x0003U | 0x0800U,
	PAGE_PROGRAM  = 0x0002U | 0x0800U,
	SECTOR_ERASE  = 0x0020U | 0x0800U,
	CHIP_ERASE    = 0x0060U,
	READ_ID       = 0x009FU,
	READ_SFDP     = 0x005AU | 0x0800U | 0x0100U,
};

enum struct fpga_cmd_t : std::uint8_t {
	NOP            = 0xFFU,
	READ_ID        = 0xE0U,
	READ_STATUS    = 0x3CU,
	CHECK_BUSY     = 0xF0U,
	ENABLE         = 0xC6U,
	ENABLE_TRANS   = 0x74U,
	DISABLE        = 0x26U,
	YEET_BITSTREAM = 0x7AU,
};

[[nodiscard]]
static std::uint8_t flash_xfr(const std::uint8_t data = 0x00U) noexcept;
static void flash_setup_xfr(const flash_cmd_t command, const std::uint32_t addr = 0x0000'0000U) noexcept;
static void flash_run_cmd(const flash_cmd_t command, const std::uint32_t addr = 0x0000'0000U) noexcept;

[[nodiscard]]
static std::uint8_t fpga_xfr(const std::uint8_t data = 0x00U) noexcept;
[[nodiscard]]
static bool fpga_program_status() noexcept;

static void fpga_cmd_read(const fpga_cmd_t command, std::span<std::uint8_t> data) noexcept;
static void fpga_cmd_write(const fpga_cmd_t command, const std::span<std::uint8_t>& data) noexcept;

static void psram_setup_xfr(const flash_cmd_t command, const std::uint32_t addr = 0x0000'0000U) noexcept;
static void psram_run_cmd(const flash_cmd_t command, const std::uint32_t addr = 0x0000'0000U) noexcept;

[[nodiscard]]
std::array<std::uint8_t, 3> read_flash_id() noexcept;
[[nodiscard]]
std::array<std::uint8_t, 8> read_psram_id() noexcept;
[[nodiscard]]
fpga_id_t read_fpga_id() noexcept;
static fpga_id_t active_fpga_id{};

static std::array<std::uint8_t, 1_KiB> spi_buffer{{}};

static void setup_fpga_pins() noexcept {

	/* Set up PSRAM Chip select is inverted */
	PORTA.set_low(pin::PSRAM_CS);
	PORTA.set_output(pin::PSRAM_CS);

	/* Set up FPGA SPI Bus */
	PORTA.set_high(pin::FPGA_CS);
	PORTA.set_output(pin::FPGA_CS);

	PORTA.set_low(pin::FPGA_CLK);
	PORTA.set_output(pin::FPGA_CLK);

	PORTA.set_low(pin::FPGA_COPI);
	PORTA.set_output(pin::FPGA_COPI);
	PORTA.setup_pin(pin::FPGA_CIPO, false, true, false, false, port_t::pin_func_t::A);
	PORTA.set_input(pin::FPGA_CIPO);
}

static void setup_flash_pins() noexcept {

	PORTA.setup_pin(pin::FLASH_CS, false, false, false, false, port_t::pin_func_t::C);
	PORTA.set_high(pin::FLASH_CS);
	PORTA.set_output(pin::FLASH_CS);

	PORTA.setup_pin(pin::FLASH_CLK, true,  false, false, false, port_t::pin_func_t::D);
	PORTA.set_output(pin::FLASH_CLK);

	PORTA.setup_pin(pin::FLASH_COPI, true,  false, false, false, port_t::pin_func_t::C);
	PORTA.set_output(pin::FLASH_COPI);

	PORTA.setup_pin(pin::FLASH_CIPO, true,  true,  false, false, port_t::pin_func_t::D);
	PORTA.set_input(pin::FLASH_CIPO);
}


static void setup_sercom() noexcept {
	/* Check if by some change the SERCOM is enabled, if so, disable it */
	if (SERCOM0_SPI.enabled()) {
		SERCOM0_SPI.disable();
	}

	setup_flash_pins();

	SERCOM0_SPI.configure(
		sercom_spi_t::mode_t::Controller,
		/* PAD0 = COPI; PAD1 = CLK; PAD2 = CS; PAD3 = CIPO */
		sercom_spi_t::dopo_t::CFG0, sercom_spi_t::dipo_t::PAD3,
		sercom_spi_t::form_t::SPI,
		sercom_spi_t::cpha_t::SAMPLE_TRAILING, sercom_spi_t::cpol_t::IDLE_LOW,
		sercom_spi_t::dord_t::MSB
	);

	/* Set the SERCOM baud */
	/* baud = (32MHz / (2 * 16MHz)) - 1 = 0 */
	SERCOM0_SPI.baud = 0U;

	SERCOM0_SPI.ctrlb = (0U << 0U) | (1U << 17U);

	while (SERCOM0_SPI.sync_busy_ctrlb()) {
		continue;
	}

	/* Enable the SERCOM */
	SERCOM0_SPI.enable();
}

bool setup_spi() noexcept {
	setup_sercom();
	setup_fpga_pins();

	const auto flash_id{read_flash_id()};

	/* Ensure we get the expected ID from the flash */
	if (flash_id != decltype(flash_id){{0xC8U, 0x40U, 0x17U}}) {
		active_fault = fault_code_t::SPI_FLASH_BAD;
		return false;
	}


	const auto psram_id{read_psram_id()};
	const auto psram_size{std::uint8_t((psram_id[2] & 0xE0U) >> 5U)};
	if (psram_id[0] != 0x9D /* ISSI */ || psram_size != 2U /* 32Mb */) {
		active_fault = fault_code_t::SPI_PSRAM_BAD;
		return false;
	}

	fpga_enter_cfg();

	// Cache the ID of the FPGA that is attached to the board
	active_fpga_id = read_fpga_id();

	if (!((active_fpga_id == fpga_id_t::LEF5UM45) || (active_fpga_id == fpga_id_t::LEF5UM5G45))) {
		active_fault = fault_code_t::FPGA_ID_BAD;
		return false;
	}

	return true;
}

[[nodiscard]]
static std::uint8_t flash_xfr(const std::uint8_t data) noexcept {

	SERCOM0_SPI.data = data;

	while (!SERCOM0_SPI.receive_complete()) {
		continue;
	}

	return std::uint8_t(SERCOM0_SPI.data);
}

static void flash_setup_xfr(const flash_cmd_t command, const std::uint32_t addr) noexcept {
	PORTA.set_low(pin::FLASH_CS);

	const auto opcode{std::uint8_t(command)};

	[[maybe_unused]]
	auto _{flash_xfr(opcode)};

	if ((static_cast<std::uint16_t>(command) & 0x0800U) == 0x0800U) {
		_ = flash_xfr(std::uint8_t(addr >> 16U));
		_ = flash_xfr(std::uint8_t(addr >>  8U));
		_ = flash_xfr(std::uint8_t(addr >>  0U));
	}

	/* Wiggle out the intersticial bytes between addr and data phase */
	const std::size_t inter_len{(static_cast<std::uint16_t>(command) & 0x0700U) >> 8U};
	for (std::size_t ctr{}; ctr < inter_len; ++ctr) {
		_ = flash_xfr();
	}
}

/* Run a flash command */
static void flash_run_cmd(const flash_cmd_t command, const std::uint32_t addr) noexcept {
	flash_setup_xfr(command, addr);
	PORTA.set_high(pin::FLASH_CS);
}

[[nodiscard]]
std::array<std::uint8_t, 3> read_flash_id() noexcept {
	std::array<std::uint8_t, 3> id;

	flash_setup_xfr(flash_cmd_t::READ_ID);

	for (auto& byte : id) {
		byte = flash_xfr();
	}

	PORTA.set_high(pin::FLASH_CS);

	return id;
}

void read_flash(const std::uint32_t addr, std::span<std::uint8_t> buffer) noexcept {
	flash_setup_xfr(flash_cmd_t::READ, addr);

	for (auto& data : buffer) {
		data = flash_xfr();
	}

	PORTA.set_high(pin::FLASH_CS);
}

void erase_flash(const std::uint32_t addr, const std::size_t length) noexcept {

	const auto aligned_addr{addr & 0xFFF000U};
	const auto addr_ovfl{addr & 0x000FFFU};
	const auto erase_len{length + addr_ovfl};

	for (std::size_t idx{}; idx < erase_len; idx += 4_KiB) {
		/* Ensure we can blow up the sector */
		flash_run_cmd(flash_cmd_t::WRITE_ENABLE);
		/* Actually do the deed */
		flash_run_cmd(flash_cmd_t::SECTOR_ERASE, aligned_addr + idx);

		/* Read back the status register and wait for BSY and WE to go low */
		flash_setup_xfr(flash_cmd_t::READ_STATUS);
		while (flash_xfr() & 0x03U) {
			continue;
		}

		PORTA.set_high(pin::FLASH_CS);
	}
}

void write_flash(const std::uint32_t addr, const std::span<std::uint8_t>& buffer) noexcept {

	/* Clear out the needed pages prior to writing */
	erase_flash(addr, buffer.size_bytes());

	for (std::size_t off{}; off < buffer.size_bytes(); off += 256) {
		flash_run_cmd(flash_cmd_t::WRITE_ENABLE);

		flash_setup_xfr(flash_cmd_t::PAGE_PROGRAM, addr + off);

		for (const auto byte : buffer.subspan(off, 256)) {
			[[maybe_unused]]
			const auto _{flash_xfr(byte)};
		}

		PORTA.set_high(pin::FLASH_CS);


		flash_setup_xfr(flash_cmd_t::READ_STATUS);
		while (flash_xfr() & 0x03U) {
			continue;
		}

		PORTA.set_high(pin::FLASH_CS);
	}
}

static void psram_setup_xfr(const flash_cmd_t command, const std::uint32_t addr) noexcept {
	PORTA.set_high(pin::PSRAM_CS);

	const auto opcode{std::uint8_t(command)};

	[[maybe_unused]]
	auto _{fpga_xfr(opcode)};

	if ((static_cast<std::uint16_t>(command) & 0x0800U) == 0x0800U) {
		_ = fpga_xfr(std::uint8_t(addr >> 16U));
		_ = fpga_xfr(std::uint8_t(addr >>  8U));
		_ = fpga_xfr(std::uint8_t(addr >>  0U));
	} else if (command == flash_cmd_t::READ_ID) {
		/* We need to fill the ADDR slot with 0's for the PSRAM */
		_ = fpga_xfr();
		_ = fpga_xfr();
		_ = fpga_xfr();
	}

	/* Wiggle out the intersticial bytes between addr and data phase */
	const std::size_t inter_len{(static_cast<std::uint16_t>(command) & 0x0700U) >> 8U};
	for (std::size_t ctr{}; ctr < inter_len; ++ctr) {
		_ = fpga_xfr();
	}
}

static void psram_run_cmd(const flash_cmd_t command, const std::uint32_t addr) noexcept {
	psram_setup_xfr(command, addr);
	PORTA.set_low(pin::PSRAM_CS);
}

std::uint32_t read_psram(std::uint32_t addr, std::span<std::uint8_t> buffer) noexcept {
	psram_setup_xfr(flash_cmd_t::READ, addr);

	for (auto& data : buffer) {
		data = fpga_xfr();
	}

	PORTA.set_low(pin::PSRAM_CS);
	return addr + buffer.size_bytes();
}

std::uint32_t write_psram(std::uint32_t addr, const std::span<std::uint8_t>& buffer) noexcept {
	for (std::size_t off{}; off < buffer.size_bytes(); off += 256) {
		psram_setup_xfr(flash_cmd_t::PAGE_PROGRAM, addr + off);

		for (const auto byte : buffer.subspan(off, 256)) {
			[[maybe_unused]]
			const auto _{fpga_xfr(byte)};
		}

		PORTA.set_low(pin::PSRAM_CS);


		psram_setup_xfr(flash_cmd_t::READ_STATUS);
		while (fpga_xfr() & 0x03U) {
			continue;
		}

		PORTA.set_low(pin::PSRAM_CS);
	}

	return addr + buffer.size_bytes();
}

[[nodiscard]]
std::array<std::uint8_t, 8> read_psram_id() noexcept {
	std::array<std::uint8_t, 8> id;

	psram_setup_xfr(flash_cmd_t::READ_ID);

	for (auto& byte : id) {
		byte = fpga_xfr();
	}

	PORTA.set_low(pin::PSRAM_CS);

	return id;
}


[[nodiscard]]
fpga_id_t read_fpga_id() noexcept {
	std::array<std::uint8_t, 4> id;

	fpga_cmd_read(fpga_cmd_t::READ_ID, {id});

	return static_cast<fpga_id_t>(read_be(id));
}

static void fpga_begin_cmd(const fpga_cmd_t command) noexcept {
	const auto cmd{static_cast<std::uint8_t>(command)};

	PORTA.set_low(pin::FPGA_CS);

	[[maybe_unused]]
	auto _{fpga_xfr(cmd)};
	/* Dummy Cycle */
	_ = fpga_xfr();
	_ = fpga_xfr();
	_ = fpga_xfr();

};

static void fpga_cmd_run(const fpga_cmd_t command) noexcept {
	fpga_begin_cmd(command);
	PORTA.set_high(pin::FPGA_CS);
}

static void fpga_cmd_read(const fpga_cmd_t command, std::span<std::uint8_t> data) noexcept {
	fpga_begin_cmd(command);

	for (auto& byte : data) {
		byte = fpga_xfr();
	}

	PORTA.set_high(pin::FPGA_CS);
}

static void fpga_cmd_write(const fpga_cmd_t command, const std::span<std::uint8_t>& data) noexcept {
	fpga_begin_cmd(command);

	for (const auto& byte : data) {
		[[maybe_unused]]
		auto _{fpga_xfr(byte)};
	}

	PORTA.set_high(pin::FPGA_CS);
}


[[nodiscard]]
static std::uint8_t fpga_xfr(const std::uint8_t data) noexcept {
	std::uint8_t res{};

	for (std::size_t bit{}; bit < 8U; ++bit) {
		PORTA.set_low(pin::FPGA_CLK);

		PORTA.set_value((data >> (7U - bit)) & 0b1, pin::FPGA_COPI);

		/* High tech delay */
		asm (R"(
			nop
			nop
		)");

		PORTA.set_high(pin::FPGA_CLK);

		res |= std::uint8_t(PORTA.pin_state(pin::FPGA_CIPO) << (7U - bit));
	}

	PORTA.set_low(pin::FPGA_CLK);

	return res;
}

static bool fpga_segmented_xfer(const std::span<std::uint8_t>& buffer) noexcept {
	PORTA.set_high(pin::FPGA_HOLD);

	for (const auto& byte : buffer) {
		[[maybe_unused]]
		auto _{fpga_xfr(byte)};
	}

	// TODO(aki): Ditto
	PORTA.set_low(pin::FPGA_HOLD);

	return true;
}

static bool fpga_program_status() noexcept {
	std::array<std::uint8_t, 4> fpga_status_bytes{};
	fpga_cmd_read(fpga_cmd_t::READ_STATUS, {fpga_status_bytes});
	const auto fpga_status{read_be(fpga_status_bytes)};

	const auto bse_err_code{std::uint8_t((fpga_status & (0x7 << 23U)) >> 23U)};

	if (fpga_status & (1U << 27U) || bse_err_code == 0b001) {
		active_fault = fault_code_t::FPGA_BIT_MISMATCH;
		return false;
	}

	if (!PORTA.pin_state(pin::FPGA_INIT)) {
		active_fault = fault_code_t::FPGA_CFG_FAILED;
		return false;
	}

	return true;
}

bool load_bitstram_psram() noexcept {
	slot_header_t header;
	[[maybe_unused]]
	auto next_addr{read_psram(0x0000'0000, spi_buffer)};

	memcpy(spi_buffer.data(), &header, sizeof(header));

	if (!header.is_valid(active_fpga_id)) {
		return false;
	}

	const auto bit_len{header.bitstream_len()};

	/* Force the FPGA to stop what it's doing and enter config mode */
	fpga_enter_cfg();

	/* Tell the FPGA we're going to shove a bitstream in it's face */
	fpga_cmd_run(fpga_cmd_t::ENABLE);
	fpga_begin_cmd(fpga_cmd_t::YEET_BITSTREAM);

	/* First partial segmented transfer of the bitstream to the FPGA */
	const auto bit_off{spi_buffer.size() - sizeof(header)};
	fpga_segmented_xfer(std::span{spi_buffer}.subspan(sizeof(header), bit_off));

	/* Transfer the rest over in 1KiB pages up to the end */
	for (std::size_t offset{bit_off}; offset < bit_len; offset += 1_KiB) {
		const auto buff_amount{std::min(std::uint32_t(bit_len - offset), 1_KiB)};
		next_addr = read_psram(next_addr, spi_buffer);
		fpga_segmented_xfer(std::span{spi_buffer}.subspan(0, buff_amount));
	};

	/* Ensure the FPGA is released from the hold */
	PORTA.set_high(pin::FPGA_HOLD);
	PORTA.set_low(pin::FPGA_CS);

	if (!fpga_program_status() ) {
		return false;
	}

	fpga_cmd_run(fpga_cmd_t::DISABLE);

	if (!PORTA.pin_state(pin::FPGA_DONE)) {
		active_fault = fault_code_t::FPGA_CFG_FAILED;
		return false;
	}

	return true;
}

bool load_bitstream_flash(std::uint8_t slot_index) noexcept {
	if (slot_index > 3) {
		active_fault = fault_code_t::SLOT_INDEX_BAD;
		return false;
	}

	std::uint32_t slot_addr{slot_index * 2_MiB};

	slot_header_t slot_header{};
	read_flash(slot_addr, {reinterpret_cast<std::uint8_t*>(&slot_header), sizeof(slot_header)});

	if (!slot_header.is_valid(active_fpga_id)) {
		return false;
	}

	const auto bit_len{slot_header.bitstream_len()};

	/* Check if the FPGA is in configuration mode, if not, bail */
	if (PORTA.pin_state(pin::FPGA_DONE) || !PORTA.pin_state(pin::FPGA_INIT)) {
		active_fault = fault_code_t::FPGA_CFG_INVALID;
		return false;
	}

	/* Advance past the slot header to the start of the bitstream */
	slot_addr += sizeof(slot_header);

	/* Tell the FPGA we're going to shove a bitstream in it's face */
	fpga_cmd_run(fpga_cmd_t::ENABLE);

	fpga_begin_cmd(fpga_cmd_t::YEET_BITSTREAM);

	for (std::size_t offset{}; offset < bit_len; offset += 1_KiB) {
		read_flash(slot_addr + offset, spi_buffer);

		const auto buff_amount{std::min(std::uint32_t(bit_len - offset), 1_KiB)};

		for (const auto& byte : std::span{spi_buffer.data(), buff_amount}) {
			[[maybe_unused]]
			auto _{fpga_xfr(byte)};
		}

	};

	PORTA.set_high(pin::FPGA_CS);

	if (!fpga_program_status() ) {
		return false;
	}

	fpga_cmd_run(fpga_cmd_t::DISABLE);

	if (!PORTA.pin_state(pin::FPGA_DONE)) {
		active_fault = fault_code_t::FPGA_CFG_FAILED;
		return false;
	}

	return true;
}

[[nodiscard]]
bool move_to_slot(std::uint8_t slot_index, std::uint16_t expected_len) noexcept {
	slot_header_t header;
	[[maybe_unused]]
	auto next_addr{read_psram(0x0000'0000, spi_buffer)};

	memcpy(spi_buffer.data(), &header, sizeof(header));

	if (!header.is_valid(active_fpga_id)) {
		return false;
	}

	const auto bit_len{header.bitstream_len()};

	/* Check that the slot header and the size of the data we want agree */
	if (bit_len != expected_len) {
		active_fault = fault_code_t::SLOT_SIZE_MISMATCH;
		return false;
	}

	std::uint32_t slot_addr{slot_index * 2_MiB};

	/* Transfer the slot over in 1KiB pages */
	for (std::size_t offset{0}; offset < bit_len; offset += 1_KiB) {
		const auto buff_amount{std::min(std::uint32_t(bit_len - offset), 1_KiB)};
		next_addr = read_psram(next_addr, spi_buffer);
		write_flash((slot_addr + offset), std::span{spi_buffer}.subspan(0, buff_amount));
	};

	return true;
}

[[nodiscard]]
std::uint8_t read_squishy_register(const std::uint8_t addr) noexcept {

	PORTA.set_low(pin::FPGA_CS);
	[[maybe_unused]]
	auto _{fpga_xfr(addr)};

	const auto val{fpga_xfr(0U)};

	PORTA.set_high(pin::FPGA_CS);

	return val;
}

void write_squishy_register(const std::uint8_t addr, const std::uint8_t val) noexcept {
	PORTA.set_low(pin::FPGA_CS);

	[[maybe_unused]]
	auto _{fpga_xfr(addr)};
	_ = fpga_xfr(val);

	PORTA.set_high(pin::FPGA_CS);
}
