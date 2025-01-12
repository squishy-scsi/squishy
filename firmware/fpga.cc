/* SPDX-License-Identifier: BSD-3-Clause */

#include "peripherals.hh"
#include "pindefs.hh"
#include "flash.hh"
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

	if (squishy_irq == 0xFFU) {
		/* Check to make sure we're not just wiggled by a glitch */
		if (!PORTA.pin_state(pin::SU_ATTN)) {
			/* The SU_ATTN line is held for the duration of the IRQ, if it's low now then we glitched */
			return true;
		}
		/* Invalid IRQ Response, bail */
		active_fault = fault_code_t::SQUISHY_IRQ_RESP_BAD;
		return false;
	}

	if (squishy_irq & squishy::registers::IRQ_WANT_DFU) {
		/* FPGA wants to be in bootloader mode, yeet it. */
		fpga_enter_cfg();
		return load_bitstream_flash(squishy::slots::BOOTLOADER);
	} else if (squishy_irq & squishy::registers::IRQ_WRITE_SLOT) {
		/* FPGA as written the target slot and payload size, retrieve them */
		const auto slot{std::uint8_t(
			(read_squishy_register(squishy::registers::SLOT) & squishy::registers::SLOT_DEST_MASK) >> 4U
		)};
		const auto txlen{[](){
			const auto low{read_squishy_register(squishy::registers::TXLEN_LOW)};
			const auto high{read_squishy_register(squishy::registers::TXLEN_HIGH)};
			return std::uint16_t((high << 8U) | low);
		}()};
		/* Let the FPGA know we're good to go */
		write_squishy_register(squishy::registers::CTRL, squishy::registers::CTRL_IRQ_ACK);

		/* Check if the slot is ephemeral or not */
		if (slot != squishy::slots::REV2_EPHEMERAL) {
			/* We need to slurp the yummy data from the PSRAM and spit it to the FLASH */
			if(!move_to_slot(slot, txlen - sizeof(slot_header_t))) {
				/* We expect that `move_to_slot` set the fault code */
				return false;
			}
		}

		/* Tell the FPGA we're done */
		write_squishy_register(squishy::registers::CTRL, squishy::registers::CTRL_WRITE_DONE);

		/* Now we wait for the boot IRQ */
	} else if (squishy_irq & squishy::registers::IRQ_BOOT) {
		const auto slot{std::uint8_t(
			read_squishy_register(squishy::registers::SLOT) & squishy::registers::SLOT_BOOT_MASK
		)};

		/* Toss the FPGA into configuration mode */
		fpga_enter_cfg();
		/* Check if we need to load the bitstream from PSRAM or flash */
		if (slot != squishy::slots::REV2_EPHEMERAL) {
			/* Load th FPGA with the slot from flash */
			return load_bitstream_flash(slot);
		} else {
			/* We *are* in the ephemeral slot, dump the slot in PSRAM to the FPGA directly */
			return load_bitstream_psram();
		}
	}

	return true;
}
