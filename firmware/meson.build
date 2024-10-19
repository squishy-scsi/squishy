# SPDX-License-Identifier: BSD-3-Clause
project(
	'Squishy Supervisor',
	'cpp',
	default_options: [
		'buildtype=debugoptimized',
		'cpp_std=c++23',
		'cpp_rtti=false',
		'cpp_eh=none',
		'warning_level=3',
		'b_ndebug=if-release',
		'b_lto=true',
		'strip=false',
	],
	license: 'BSD-3-Clause',
	version: '0.1.0',
	meson_version: '>= 1.4.0'
)

cpp_std = get_option('cpp_std')

cxx_native = meson.get_compiler('cpp', native: true)
cxx_target = meson.get_compiler('cpp', native: false)

if cpp_std not in ['c++20', 'c++23', 'gnu++20', 'gnu++23']
	error(f'Unsupported C++ Version @cpp_std@, must be c++20/gnu++20 or newer')
endif

if not meson.is_cross_build()
	error('Firmware only supports cross-build, re-invoke with a cross file')
endif

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
        '-Werror=return-type',
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
        '-Wredundant-decls',
        '-Wvla',
        '-Wstack-protector',
        '-Wunsuffixed-float-constant',
        '-Wimplicit-fallthrough',
        '-Wxor-used-as-pow',
        '-Wself-move',
        '-Wdangling-reference',
        '-Werror=switch',
        '-Wpadded',
]

message('Setting up native compiler warnings')
add_project_arguments(
        cxx_native.get_supported_arguments(extended_warnings),
        language: 'cpp',
        native: true
)

message('Setting up target compiler warnings')
add_project_arguments(
        cxx_target.get_supported_arguments(extended_warnings),
        language: 'cpp',
        native: false
)

py = import('python')
py = py.find_installation(
        'python3',
        required: true,
        modules: [],
)

fs = import('fs')

git     = find_program('git',     required: false, native: true )

objcopy = find_program('objcopy', required: true,  native: false)
objdump = find_program('objdump', required: true,  native: false)
strip   = find_program('strip',   required: true,  native: false)
size    = find_program('size',    required: true,  native: false)

source_dir = meson.project_source_root()

common_args = [
	'-ffreestanding', '-nostdlib', '-nostartfiles', '-mthumb', '-mcpu=cortex-m0plus',
        '-fno-exceptions', '-fno-rtti'
]

compile_args = [

] + common_args

ld_args = [
	f'-T@source_dir@/atsamd09.ld', '-Wl,--gc-sections', '-Wl,--print-memory-usage'
] + common_args

firmware_srcs = files([
	'main.cc',
        'spi.cc',
	'startup.cc',
        'memory.cc',
        'timing.cc',
        'atomic.cc',
])

firmware_full = executable(
	'squishy-supervisor',
	firmware_srcs,
	include_directories: [
		include_directories('.'),
	],
	name_suffix: 'elf',
	cpp_args: compile_args,
	link_args: ld_args,
        link_depends: files('atsamd09.ld'),
	gnu_symbol_visibility: 'inlineshidden',
	implicit_include_directories: false,
	native: false,
)

firmware_symbols = custom_target(
	'squishy-supervisor-syms',
	input: firmware_full,
	output: 'squishy-supervisor.syms',
	command: [ objcopy, '--only-keep-debug', '@INPUT@', '@OUTPUT@' ]
)

firmware_stripped = custom_target(
	'squishy-supervisor-stripped',
	input: firmware_full,
	output: 'squishy-supervisor.stripped.elf',
	command: [ strip, '--strip-debug', '--strip-unneeded', '@INPUT@', '-o', '@OUTPUT@' ]
)
