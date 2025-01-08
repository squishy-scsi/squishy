/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>

#include <exception>

#include "units.hh"
#include "platform.hh"
#include "peripherals.hh"
#include "pindefs.hh"
#include "fault.hh"
#include "fpga.hh"
#include "spi.hh"

std::atomic<std::uint8_t> extint{0U};

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
	PORTA.setup_pin(pin::DFU_BTN, true, false, false, false, port_t::pin_func_t::A);
	PORTA.set_input(pin::DFU_BTN);
	/* Setup FPGA Side attention lines */
	PORTA.setup_pin(pin::SU_ATTN, true, false, false, false, port_t::pin_func_t::A);
	PORTA.set_input(pin::SU_ATTN);

	/* SPI Bus hold line */
	PORTA.setup_pin(pin::BUS_HOLD, false, true, false, false, port_t::pin_func_t::A);
	PORTA.set_input(pin::BUS_HOLD);
}

void setup_clocking() noexcept {
	/* TODO(aki): Setup the PLL so we can boost our core clock to 48MHz */

	/* Set GCLK0 to use the external clock input on PA08 */
	GCLK.config_gen(gclk_t::clkgen_t::GCLK0, gclk_t::clksrc_t::GCLKIN, true);

	/* Enable SERCOM0 clocking */
	PM.unmask(pm_t::apbc_periph_t::SERCOM0);

	/* Set SERCOM0_CORE to GCLK0 */
	GCLK.config_clk(gclk_t::clkid_t::SERCOM0_CORE, gclk_t::clkgen_t::GCLK0, true, false);
	/* Set SERCOMx_SLOW to GCLK0 */
	GCLK.config_clk(gclk_t::clkid_t::SERCOMx_SLOW, gclk_t::clkgen_t::GCLK0, true, false);

	/* Enable the EIC */
	PM.unmask(pm_t::apba_periph_t::EIC);
	GCLK.config_clk(gclk_t::clkid_t::EIC, gclk_t::clkgen_t::GCLK0, true, false);
}

void setup_extint() noexcept {

	/* Configure the EXTINTS */

	/* SU_ATTN line */
	EIC.enable_extint_irq(1U);
	EIC.enable_extint(1U, false, eic_t::sense_t::RISE);

	/* DFU_TRIG line */
	EIC.enable_extint_irq(7U);
	EIC.enable_extint(7U, true, eic_t::sense_t::RISE); // When button is released

	/* Finally, enable the EIC */
	EIC.enable();
}

void start() noexcept {
	/* Brown-out detect @ 1v7 ± 50mV */
	SYSCTRL.enable_bod33(7U);
	/* This will do until BOD is configured */
	if (PM.was_brownout()) {
		DSU.reset_core();
	}

	setup_io();
	setup_clocking();
	setup_extint();
	setup_fpga_ctrl_pins();

	/* Ensure SysTick keeps running when we call std::terminate() so we can blink a panic code  */
	NVIC.set_priority(15, nvic_t::priority_t::TOP);

	SYSTICK.reload_value = (32_MHz / 1_kHz) - 1U;
	SYSTICK.enable();

	/* If we can't initialize SPI, then we're SOL, so bail */
	if (!setup_spi()) {
		std::terminate();
	}

	/* Try to load the first applet */
	if (!load_bitstream_flash(squishy::slots::APPLET1)) {
		/* We *might* still be okay, clear the fault code and try to load the bootloader */
		active_fault = fault_code_t::NONE;
		if (!load_bitstream_flash(squishy::slots::BOOTLOADER)) {
			/* Well shit,,, */
			std::terminate();
		}
	}

	for(;;) {
		const auto interrupts{extint.exchange(0U)};

		if (interrupts != 0) {
			/* Someone pressed the DFU button (EXTINT1) */
			if (interrupts & (1U << 1U)) {
				fpga_enter_cfg();
				/* Load the bootloader bitstream */
				if (!load_bitstream_flash(squishy::slots::BOOTLOADER)) {
					std::terminate();
				}
			}

		}

		asm ("wfi"); // Wiggle for interrupt:tm:
	}
}

void irq_eic() noexcept {
	/* Get the triggered EXTINTs */
	const auto intnum{EIC.get_extint_irq()};

	/* Set which interrupts were triggered */
	extint = intnum;

	/* ACK triggered interrupts */
	for (std::size_t i{0U}; i < 8U; ++i) {
		const auto was_enabled{static_cast<bool>(std::uint32_t(intnum >> i) & 0b1U)};
		if (was_enabled) {
			EIC.ack_extint(static_cast<std::uint8_t>(i));
		}
	}
}
