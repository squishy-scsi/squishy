/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>

#include "spi.hh"

#include "peripherals.hh"
#include "pindefs.hh"
#include "units.hh"
#include "timing.hh"
#include "flash.hh"

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

static void fpga_cmd_read(const fpga_cmd_t command, std::span<std::uint8_t> data) noexcept;
static void fpga_cmd_write(const fpga_cmd_t command, const std::span<std::uint8_t>& data) noexcept;

[[nodiscard]]
std::array<std::uint8_t, 3> read_jedec_id() noexcept;

[[nodiscard]]
fpga_id_t read_fpga_id() noexcept;
static fpga_id_t active_fpga_id{};

static std::array<std::uint8_t, 1_KiB> spi_buffer{{}};

static void setup_fpga_pins() noexcept {

	/* Set up PSRAM Chip select */
	PORTA.set_high(pin::PSRAM_CS);
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


	/* Setup FPGA Config Signals */
	PORTA.set_high(pin::FPGA_HOLD);
	PORTA.set_high(pin::FPGA_PROG);

	PORTA.setup_pin(pin::FPGA_INIT, false, true, false, false, port_t::pin_func_t::A);
	PORTA.set_input(pin::FPGA_INIT);

	PORTA.set_output(pin::FPGA_HOLD);
	PORTA.set_output(pin::FPGA_PROG);

	PORTA.setup_pin(pin::FPGA_DONE, false, true, false, false, port_t::pin_func_t::A);
	PORTA.set_input(pin::FPGA_DONE);
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

static void setup_fpga() noexcept {
	setup_fpga_pins();
}

static void fpga_enter_cfg() noexcept {
	PORTA.set_low(pin::FPGA_PROG);
	delay(1);
	PORTA.set_high(pin::FPGA_PROG);
	delay(50);
}

bool setup_spi() noexcept {
	setup_sercom();
	setup_fpga();

	const auto flash_id{read_jedec_id()};

	/* Ensure we get the expected ID from the flash */
	if (flash_id != decltype(flash_id){{0xC8U, 0x40U, 0x17U}}) {
		PORTA.set_low(pin::SU_LED_R);
		return false;
	}

	fpga_enter_cfg();

	// Cache the ID of the FPGA that is attached to the board
	active_fpga_id = read_fpga_id();

	if (active_fpga_id != fpga_id_t::LEF5UM45) {
		PORTA.set_low(pin::SU_LED_R);
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
std::array<std::uint8_t, 3> read_jedec_id() noexcept {
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

[[nodiscard]]
fpga_id_t read_fpga_id() noexcept {
	std::array<std::uint8_t, 4> id;

	fpga_cmd_read(fpga_cmd_t::READ_ID, {id});

	return static_cast<fpga_id_t>(read_be(id));
}

static void fpga_cmd_read(const fpga_cmd_t command, std::span<std::uint8_t> data) noexcept {
	const auto cmd{static_cast<std::uint8_t>(command)};

	PORTA.set_low(pin::FPGA_CS);

	[[maybe_unused]]
	auto _{fpga_xfr(cmd)};
	/* Dummy Cycle */
	_ = fpga_xfr();
	_ = fpga_xfr();
	_ = fpga_xfr();

	for (auto& byte : data) {
		byte = fpga_xfr();
	}

	PORTA.set_high(pin::FPGA_CS);
}

static void fpga_cmd_write(const fpga_cmd_t command, const std::span<std::uint8_t>& data) noexcept {
	const auto cmd{static_cast<std::uint8_t>(command)};

	PORTA.set_low(pin::FPGA_CS);

	[[maybe_unused]]
	auto _{fpga_xfr(cmd)};
	/* Dummy Cycle */
	_ = fpga_xfr();
	_ = fpga_xfr();
	_ = fpga_xfr();

	for (const auto& byte : data) {
		_ = fpga_xfr(byte);
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
