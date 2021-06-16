# SPDX-License-Identifier: BSD-3-Clause
project(
	'squishy',
	'cpp',
	default_options: [
		'warning_level=3',
		'cpp_std=c++17',
		'b_ndebug=if-release',
		'b_lto=true',
	],
	license: 'BSD-3-Clause',
	version: '0.0.1',
	subproject_dir: 'deps'
)

cxx_c = meson.get_compiler('cpp', native: true)
cxx_n = meson.get_compiler('cpp', native: false)

extended_warnings = [
	'-Wdouble-promotion',
	'-Wformat=2',
	'-Wformat-overflow=2',
	'-Wformat-signedness',
	'-Wformat-truncation',
	'-Wnull-dereference',
	'-Wmissing-attributes',
	'-Wmissing-braces',
	'-Wsequence-point',
	'-Wreturn-type',
	'-Wunused',
	'-Wunused-local-typedefs',
	'-Wunused-const-variable=2',
	'-Wmaybe-uninitialized',
	'-Wunknown-pragmas',
	'-Wstrict-aliasing',
	'-Wstrict-overflow=3',
	'-Wstring-compare',
	'-Wstringop-overflow',
	'-Warith-conversion',
	'-Wvla-parameter',
	'-Wduplicated-branches',
	'-Wshadow=local',
	'-Wunsafe-loop-optimizations',
	'-Wbad-function-cast',
	'-Wcast-qual',
	'-Wcast-align=strict',
	'-Wcast-function-type',
	'-Wconversion',
	'-Wdangling-else',
	'-Wsign-conversion',
	'-Wfloat-conversion',
	'-Wpacked',
	'-Wpadded',
	'-Wredundant-decls',
	'-Winline',
	'-Wvla',
	'-Wstack-protector',
	'-Wunsuffixed-float-constant',
	'-Wimplicit-fallthrough',
]

add_project_arguments(
	cxx_c.get_supported_arguments(extended_warnings),
	language: 'cpp'
)

add_project_arguments(
	cxx_n.get_supported_arguments(extended_warnings),
	language: 'cpp'
)

py = import('python')
py_modules = [
	'jinja2',
	'usb',
	'construct',
	'nmigen',
	'luna',
]

py_inst = py.find_installation(
	'python3',
	required: true,
	modules: py_modules,
	native: true,
)

subdir('etc')

subdir('gateware')
subdir('software')

# Generate the packed GPT/FAT16 Image

bootimg = custom_target(
	'squishy-bootimg',
	input: squish_util,
	output: 'squishy.boot',
	command: [
		py_inst.full_path(), '@INPUT@',
		'--build-dir', meson.current_build_dir(),
		'gen-boot-img',
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
	'squishy-flashimg',
	input: squish_util,
	output: 'squishy.bin',
	command: [
		py_inst.full_path(), '@INPUT@',
		'--build-dir', meson.current_build_dir(),
		'pack-image',
		'--boot-img', bootimg,
		'--bitstream', squishy_bitstream,
	],
	build_by_default: true,
	console: true,
	install: true,
	install_dir: get_option('datadir') / 'squishy',
	install_mode: 'rw-rw----'
)
