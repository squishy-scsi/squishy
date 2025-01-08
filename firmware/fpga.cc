/* SPDX-License-Identifier: BSD-3-Clause */

#include "peripherals.hh"
#include "pindefs.hh"
#include "fpga.hh"
#include "spi.hh"
#include "timing.hh"

void setup_fpga_ctrl_pins() noexcept {
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

void fpga_enter_cfg() noexcept {
	PORTA.set_low(pin::FPGA_PROG);
	delay(1);
	PORTA.set_high(pin::FPGA_PROG);
	delay(50);
}

[[nodiscard]]
bool fpga_handle_irq() noexcept {
	/*
		IRQ Register: 0bXXXXXBWD
			* B - Boot       - FPGA Wants us to boot it from the given slot
			* W - Write Slot - FPGA Wants us to write the PSRAM contents to the given slot
			* D - Want DFU   - FPGA Wants to be reloaded into the bootloader

		Slot ID 3 is the Ephemeral slot, don't write to flash, just re-program the FPGA
	*/
	const auto squishy_irq{read_squishy_register(squishy::registers::IRQ)};
	return true;
}
