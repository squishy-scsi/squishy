# SPDX-License-Identifier: BSD-3-Clause
# substrate = dependency(
# 	'substrate',
# 	required: true,
# 	version: '>=0.0.1',
# 	fallback: ['substrate', 'substrate_dep'],
# 	native: true,
# 	default_options: [
# 		'default_library=static',
# 		'build_tests=false',
# 	]
# )

uwu_efi = dependency(
	'uwu-efi',
	required: true,
	version: '>=0.0.1',
	fallback: ['uwu-efi', 'uwuefi_dep'],
	native: false,
	default_options: [
		'default_library=static',
		'build_tests=false',
		'build_uwuasm=false',
		'build_examples=false',
	]
)

subdir('slurp')
