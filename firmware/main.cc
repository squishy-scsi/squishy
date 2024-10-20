/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>

#include <exception>

#include "units.hh"
#include "platform.hh"
#include "peripherals.hh"
#include "pindefs.hh"

#include "spi.hh"

void setup_io() noexcept {
	/* Setup the global clock input */
	PORTA.setup_pin(pin::CLKIN, true, false, false, false, port_t::pin_func_t::H);
	PORTA.set_input(pin::CLKIN);

	/* Setup LEDs */
	PORTA.set_high(pin::SU_LED_G);
	PORTA.set_output(pin::SU_LED_G); /* status LED */
	PORTA.set_high(pin::SU_LED_R);
	PORTA.set_output(pin::SU_LED_R); /* error LED */

	/* Setup External DFU Trigger */
	PORTA.set_input(pin::DFU_BTN);
	/* Setup FPGA Side attention lines */
	/* TODO: This need to be EXTINTs, not normal inputs */
	PORTA.set_input(pin::DFU_TRIG);
	PORTA.set_input(pin::SU_ATTN);
}

void setup_clocking() noexcept {
	/* Set GCLK0 to use the external clock input on PA08 */
	GCLK.config_gen(gclk_t::clkgen_t::GCLK0, gclk_t::clksrc_t::GCLKIN, true);

	/* Enable SERCOM0 clocking */
	PM.unmask(pm_t::apbc_periph_t::SERCOM0);

	/* Set SERCOM0_CORE to GCLK0 */
	GCLK.config_clk(gclk_t::clkid_t::SERCOM0_CORE, gclk_t::clkgen_t::GCLK0, true, false);
	/* Set SERCOMx_SLOW to GCLK0 */
	GCLK.config_clk(gclk_t::clkid_t::SERCOMx_SLOW, gclk_t::clkgen_t::GCLK0, true, false);
}



void start() noexcept {
	setup_io();
	setup_clocking();

	SYSTICK.reload_value = (32_MHz / 1_kHz) - 1U;
	SYSTICK.enable();

	if (!setup_spi()) {
		std::terminate();
	}

	if (!load_bitstream(0)) {
		std::terminate();
	}

	for(;;) {
		PORTA.toggle(pin::SU_LED_G);
		for (std::size_t i{0z}; i < 65525*10z; ++i) {
			asm volatile ("");
		}
	}
}
