# SPDX-License-Identifier: BSD-3-Clause

import logging    as log
from pathlib      import Path
import subprocess

def _run_meson_command(run_dir: Path, command: str, options: list = []) -> bool:

	cmd = [
		'meson',
		command,
		*options
	]

	log.debug(f'Running \'{" ".join(cmd)}\' in \'{run_dir}\'')

	ret = subprocess.run(
		cmd,
		capture_output = True,
		cwd = str(run_dir)
	)

	if ret.returncode != 0:
		log.error('Configure failed!')
		log.error(ret.stderr)
		log.error(ret.stdout)
		return False
	else:
		log.debug(ret.stdout)

	return True


def configure(build_dir: Path, src_dir: Path, options: list = [])  -> bool:
	log.info(f'Configuring Meson project in {src_dir}, build dir: {build_dir}')

	if not build_dir.exists():
		build_dir.mkdir()

	return _run_meson_command(build_dir, '..', options )

def build(build_dir: Path) -> bool:

	if not build_dir.exists():
		log.error(f'Unable to build project, build directory {build_dir} does not exist')
		return False

	log.info('Building Meson project')
	return _run_meson_command(build_dir, 'compile')
