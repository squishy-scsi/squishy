# The python environment needed for nMigen
py3 = import('python').find_installation(
	'python3',
	modules: [
		'argparse',
		'nmigen',
		'luna',
	]
)

if py3.found()
	if not find_program('gtkwave', required: false).found()
		warning('Unable to find gtkwave, simulation results won\'t be able to be viewed')
	endif

	# Needed tools for nMigen
	yosys = find_program('yosys', required: true)

	lethallink_nmigen = '@0@/gateware/squishy.py'.format(meson.source_root())


	run_target(
		'gateware-synthesize',
		command: [
			py3,
			lethallink_nmigen,
			'--synthesize'
		]
	)

	run_target(
		'gateware-verify',
		command: [
			py3,
			lethallink_nmigen,
			'--verify'
		]
	)

	run_target(
		'gateware-simulate',
		command: [
			py3,
			lethallink_nmigen,
			'--simulate'
		],
	)

else
	warning('Unable to find a python 3 installation with nMigen installed, not building gateware')
endif
