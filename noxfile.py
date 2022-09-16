# SPDX-License-Identifier: BSD-3-Clause

import shutil
from pathlib import Path

import nox

BUILD_DIR = (Path.cwd() / 'build')
DOCS_DIR  = (Path.cwd() / 'docs' / 'web')

@nox.session(reuse_venv = True)
def test(session: nox.Session) -> None:
	session.install('.')
	session.run(
		'python', '-m', 'unittest', 'discover',
		'-s', 'tests'
	)

@nox.session
def docs(session: nox.Session) -> None:
	out_dir = (BUILD_DIR / 'docs')
	shutil.rmtree(out_dir, ignore_errors = True)
	session.install('-r', str(DOCS_DIR / 'requirements.txt'))
	session.install('.')
	session.run('sphinx-build', '-b', 'html', str(DOCS_DIR), str(out_dir))

@nox.session
def mypy(session: nox.Session) -> None:
	out_dir = (BUILD_DIR / 'mypy')
	session.install('mypy')
	session.install('lxml')
	session.run('mypy', '--non-interactive', '--install-types')
	session.run('mypy', '-p', 'squishy', '--html-report', str(out_dir.resolve()))

@nox.session
def flake8(session: nox.Session) -> None:
	session.install('flake8')
	session.run('flake8', './squishy')
	session.run('flake8', './tests')
