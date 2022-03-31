# SPDX-License-Identifier: BSD-3-Clause
import logging

log = logging.getLogger('squishy')

__all__ = (
	'run_sims',
)

def _collect_sims():
	import pkgutil
	from . import sim

	sims = []

	for _, name, is_pkg in pkgutil.iter_modules(path = getattr(sim, '__path__')):
		if not is_pkg:
			__import__(f'{getattr(sim, "__name__")}.{name}')
			if not hasattr(getattr(sim, name), 'DONT_LOAD'):
				sims.append({
					'name' : getattr(sim, name).SIM_NAME,
					'cases': getattr(sim, name).SIM_CASES,
				})

	return sims

def run_sims(args):
	from os import path, mkdir

	sim_dir = path.join(args.build_dir, 'sim')
	if not path.exists(sim_dir):
		mkdir(sim_dir)

	for sim in _collect_sims():
		log.info(f' => Running simulation set \'{sim["name"]}\'')

		output_dir = path.join(sim_dir, sim['name'])
		if not path.exists(output_dir):
			mkdir(output_dir)

		for case, name in sim['cases']:
			log.info(f' ===> Running \'{name}\'')

			basename = path.join(output_dir, name)

			with case.write_vcd(f'{basename}.vcd', f'{basename}.gtkw'):
				case.reset()
				case.run()
