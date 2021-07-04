# SPDX-License-Identifier: BSD-3-Clause
gateware_gen = meson.current_source_dir() / 'main.py'

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
	],
	build_by_default: true,
	build_always_stale: true,
	console: true,
	install: false,
)

nextpnr_ice40 = find_program('nextpnr-ice40', required: true)
run_target(
	'nextpnr-gui',
	command: [
		nextpnr_ice40.full_path(),
		'--gui',
		'--hx8k', '--package', 'bg121',
		'--freq', '65.00',
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
