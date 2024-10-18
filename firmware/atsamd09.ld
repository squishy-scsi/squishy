/* SPDX-License-Identifier: BSD-3-Clause */
MEMORY {
	FLASH (rx): ORIGIN = 0x00000000, LENGTH = 16K
	RAM   (rwx): ORIGIN = 0x20000000, LENGTH = 4K
}

SECTIONS {
	.text : {
		PROVIDE(text_start = .);
		KEEP(*(.nvic_table));
		*(.text.* .text .gnu.linkonce.t.*)
		*(.rodata.* .rodata .gnu.linkonce.r.*)

		. = ALIGN(4);
		/* Constructors */
		PROVIDE(ctors_start = .);
		*(.init_array.* .ctors.*)
		KEEP(*(.init_array .ctors));
		PROVIDE(ctors_end = .);

		PROVIDE(text_end = .);
	} >FLASH

	/* Don't stick anything in flash between `text_end` and `data_start`, you will regret it */

	/* We only have 4K of RAM, so a 1K stack will have to do */
	.stack : {
		. += 0x00000400;
		PROVIDE(stack_top = .);
	} >RAM

	.data : {
		PROVIDE(data_start = .);
		*(.data.* .data)
		PROVIDE(data_end = .);
	} >RAM AT >FLASH

	.bss : {
		PROVIDE(bss_start = .);
		*(.bss.* .bss)
		*(COMMON)
		PROVIDE(bss_end = .);
	} >RAM
}
