# SPDX-License-Identifier: BSD-3-Clause
gateware_gen = meson.current_source_dir() / 'main.py'

squishy_bitstream = custom_target(
	'squishy-gateware',
	input: gateware_gen,
	output: 'squishy.bit',
	command: [
		py_inst.full_path(), '@INPUT@',
		'--build-dir', meson.current_build_dir(),
	],
	build_by_default: true,
	console: true,
	install: true,
	install_dir: get_option('datadir') / 'squishy',
	install_mode: 'rw-rw----'
)

