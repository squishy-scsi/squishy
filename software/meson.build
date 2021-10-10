# SPDX-License-Identifier: BSD-3-Clause
squishy = meson.current_source_dir() / 'squishy.py'


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
	input: squishy,
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
		'gateware',
		# SCSI Configuration Options
		'--scsi-did', get_option('scsi_did').to_string(),

	] + optional_flags + [
		'build'
	],
	build_by_default: true,
	build_always_stale: true,
	console: true,
	install: false,
)

alias_target('gateware', squishy_bitstream)

run_target(
	'sim',
	command: [
		py_inst.full_path(), squishy,
		'--build-dir', meson.current_build_dir(),
		'gateware',
		# SCSI Configuration Options
		'--scsi-did', get_option('scsi_did').to_string(),

	] + optional_flags + [
		'simulate'
	],
)

run_target(
	'verify',
	command: [
		py_inst.full_path(), squishy,
		'--build-dir', meson.current_build_dir(),
		'gateware',
		# SCSI Configuration Options
		'--scsi-did', get_option('scsi_did').to_string(),

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

run_target(
	'nextpnr-cli',
	command: [
		nextpnr_ice40.full_path(),
		'--hx8k', '--package', 'bg121',
		'--pcf',  '@0@/squishy.pcf'.format(meson.current_build_dir()),
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

if get_option('taperipper')
	# Generate the packed GPT/FAT16 Image
	bootimg = custom_target(
		'taperipper-bootimg',
		input: squishy,
		output: 'taperipper.boot',
		command: [
			py_inst.full_path(), '@INPUT@',
			'--build-dir', meson.current_build_dir(),
			'taperipper',
			'build-bootimage',
			'--efi-fw', slurp
		],
		build_by_default: true,
		console: true,
		install: true,
		install_dir: get_option('datadir') / 'squishy',
		install_mode: 'rw-rw----'
	)

	# Pack the bitstream and boot image together
	flashimg = custom_target(
		'taperipper-flashimg',
		input: squishy,
		output: 'taperipper.bin',
		command: [
			py_inst.full_path(), '@INPUT@',
			'--build-dir', meson.current_build_dir(),
			'taperipper',
			'pack-flash',
			'--boot-img',   bootimg,
			'--bitstream',  squishy_bitstream,
		],
		build_by_default: true,
		console: true,
		install: true,
		install_dir: get_option('datadir') / 'squishy',
		install_mode: 'rw-rw----'
	)
endif
