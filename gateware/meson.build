# SPDX-License-Identifier: BSD-3-Clause
gateware_gen = meson.current_source_dir() / 'main.py'


optional_flags = []

if get_option('enable_uart')
	optional_flags += [
		'--enable-uart',
		'--baud',      get_option('uart_baud'),
		'--data-bits', get_option('uart_data_bits'),
		'--parity',    get_option('uart_parity'),
	]
endif



squishy_bitstream = custom_target(
	'squishy-gateware',
	input: gateware_gen,
	output: [
		'build_squishy.sh',
		'build_squishy.bat',
		'squishy.asc',
		'squishy.bin',
		'squishy.debug.v',
		'squishy.il',
		'squishy.json',
		'squishy.pcf',
		'squishy.rpt',
		'squishy.tim',
		'squishy.ys',
	],
	command: [
		py_inst.full_path(), '@INPUT@',
		'--build-dir', meson.current_build_dir(),
		# USB Configuration Options
		'--vid', get_option('vid').to_string(),
		'--pid', get_option('pid').to_string(),
		'--manufacturer',  get_option('manufacturer'),
		'--product',       get_option('product'),
		'--serial_number', get_option('serial_number'),

	] + optional_flags + [
		'build'
	],
	build_by_default: true,
	build_always_stale: true,
	console: true,
	install: false,
)

run_target(
	'sim',
	command: [
		py_inst.full_path(), gateware_gen,
		'--build-dir', meson.current_build_dir(),
		# USB Configuration Options
		'--vid', get_option('vid').to_string(),
		'--pid', get_option('pid').to_string(),
		'--manufacturer',  get_option('manufacturer'),
		'--product',       get_option('product'),
		'--serial_number', get_option('serial_number'),

	] + optional_flags + [
		'simulate'
	],
)

run_target(
	'verify',
	command: [
		py_inst.full_path(), gateware_gen,
		'--build-dir', meson.current_build_dir(),
		# USB Configuration Options
		'--vid', get_option('vid').to_string(),
		'--pid', get_option('pid').to_string(),
		'--manufacturer',  get_option('manufacturer'),
		'--product',       get_option('product'),
		'--serial_number', get_option('serial_number'),

	] + optional_flags + [
		'verify'
	],
)

nextpnr_ice40 = find_program('nextpnr-ice40', required: true)
run_target(
	'nextpnr-gui',
	command: [
		nextpnr_ice40.full_path(),
		'--gui',
		'--hx8k', '--package', 'bg121',
		'--pcf', '@0@/squishy.pcf'.format(meson.current_build_dir()),
		'--json', '@0@/squishy.json'.format(meson.current_build_dir()),
	]

)

icebox_stat = find_program('icebox_stat', required: true)
run_target(
	'gateware-stats',
	command: [
		icebox_stat.full_path(),
		meson.current_build_dir() / 'squishy.asc'
	]
)
