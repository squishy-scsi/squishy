/* SPDX-License-Identifier: BSD-3-Clause */

#include <cstdint>
#include <array>

#include "platform.hh"
#include "timing.hh"

extern "C" const std::uint32_t stack_top;
extern "C" const std::uint32_t text_end;
extern "C" std::uint32_t data_start;
extern "C" const std::uint32_t data_end;
extern "C" std::uint32_t bss_start;
extern "C" const std::uint32_t bss_end;

using ctor_func_t = void(*)();
using irq_func_t  = void(*)();

extern "C" const ctor_func_t ctors_start, ctors_end;

void irq_reset() noexcept;
void irq_nmi() noexcept;
void irq_noop() noexcept;
[[using gnu: naked, noreturn]]
void irq_fault() noexcept;

void irq_systick() noexcept;

struct nvic_table_t final {
	const void* stack_top;
	std::array<irq_func_t, 32> vector_table;
};


[[using gnu: section(".nvic_table"), used]]
static constexpr nvic_table_t nvic_table {
	&stack_top, {{
		irq_reset,
		irq_nmi,  /* External Interrupt Controller */
		irq_fault,

		/* Cortex-M Fixed Vectors  */
		nullptr,     /* Reserved */
		nullptr,     /* Reserved */
		nullptr,     /* Reserved */
		nullptr,     /* Reserved */
		nullptr,     /* Reserved */
		nullptr,     /* Reserved */
		nullptr,     /* Reserved */
		irq_noop,    /* SV Call */
		irq_noop,    /* Pend SV */
		irq_systick, /* SysTick */

		/* ATSAMD06 Vectors */
		irq_noop, /* Power Manager */
		irq_noop, /* System Control */
		irq_noop, /* Watchdog Timer */
		irq_noop, /* RTC */
		irq_noop, /* External Interrupt Controller */
		irq_noop, /* Flash Controller */
		irq_noop, /* DMA Controller */
		nullptr,  /* Reserved */
		irq_noop, /* Event System */
		irq_noop, /* SERCOM0 */
		irq_noop, /* SERCOM1 */
		nullptr,  /* Reserved */
		nullptr,  /* Reserved */
		irq_noop, /* Timer/Counter 1 */
		irq_noop, /* Timer/Counter 2 */
		irq_noop, /* ADC */
		nullptr,  /* Reserved */
		nullptr,  /* Reserved */
		nullptr,  /* Reserved */
	}}
};



void irq_reset() noexcept {
	for(;;) {
		auto* src{&text_end};

		/* Stuffing `.data` into RAM */
		for (auto* dst{&data_start}; dst < &data_end; ++dst, ++src) {
			*dst = *src;
		}
		/* Clearing out `.bss` */
		for (auto* dst{&bss_start}; dst < &bss_end; ++dst) {
			*dst = 0U;
		}
		/* Calling constructors */
		for (auto* ctor{&ctors_start}; ctor != &ctors_end; ++ctor) {
			(*ctor)();
		}

		/* enter the main firmware */
		start();
	}
}

void irq_nmi() noexcept {
	for(;;)
		continue;
}

void irq_noop() noexcept {
	for(;;)
		continue;
}

void irq_fault() noexcept {
	asm(R"(
			/* Check which operating mode we're in */
			movs 	r0, #4
			movs 	r1, lr
			tst 	r0, r1
			beq 	_MSP
			/* Extract program stack pointer */
			mrs 	r0, psp
			b _HALT
		_MSP:
			/* Extract machine stack pointer */
			mrs 	r0, msp
		_HALT:
		 	/* See ARM DDI0419E - ARMv6-M TRM B1-196 */
			ldr 	r1, [r0, #0x00] /* register 0 */
			ldr 	r2, [r0, #0x04] /* register 1 */
			ldr 	r3, [r0, #0x08] /* register 2 */
			ldr 	r4, [r0, #0x0C] /* register 3 */
			ldr 	r5, [r0, #0x10] /* register 12 */
			ldr 	r6, [r0, #0x14] /* register lr */
			ldr 	r7, [r0, #0x18] /* register pc */
			mov 	r8, r7 /* Move PC into r8 */
			ldr 	r7, [r0, #0x1C] /* register xpsr */
		_HCF:
			b _HCF
	)");
}

/* Gives us a (roughly) monotonic tick every 1ms */
void irq_systick() noexcept {
	++ms_elapsed;
}

namespace std {
	void terminate() noexcept {
		irq_fault();
	}
}
