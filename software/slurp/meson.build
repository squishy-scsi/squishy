# SPDX-License-Identifier: BSD-3-Clause

subdir('include')
subdir('resources')


slurp_srcs = files([
	'slurp.cc',
])


slurp = shared_module(
	'slurp',
    slurp_srcs,

    name_suffix: 'efi',
    name_prefix: '',

    include_directories: [
    	slurp_inc,
    	include_directories(
    		'/usr/include/efi',
    		'/usr/include/efi/x86_64',
    		'/usr/include/efi/protocol',
    	)
    ],
    install: true,
    native: false,
)
