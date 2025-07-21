# SPDX-License-Identifier: BSD-3-Clause

from os             import devnull, getenv
from pathlib        import Path

import nox
from nox.sessions   import Session

ROOT_DIR  = Path(__file__).parent

BUILD_DIR = ROOT_DIR  / 'build'
CNTRB_DIR = ROOT_DIR  / 'contrib'
DOCS_DIR  = ROOT_DIR  / 'docs'
DIST_DIR  = BUILD_DIR / 'dist'

IN_CI           = getenv('GITHUB_WORKSPACE') is not None
ENABLE_COVERAGE = IN_CI or getenv('SQUISHY_TEST_COVERAGE') is not None
SKIP_EXAMPLES   = getenv('SQUISHY_TEST_SKIP_EXAMPLES') is not None
SKIP_FORMAL     = getenv('SQUISHY_TEST_SKIP_FORMAL') is not None

# Default sessions to run
nox.options.sessions = (
	'test',
	'lint',
	'typecheck-mypy',
)


@nox.session(reuse_venv = True, venv_params = ['--system-site-packages'])
def test(session: Session) -> None:
	OUTPUT_DIR = BUILD_DIR / 'tests'
	OUTPUT_DIR.mkdir(parents = True, exist_ok = True)

	EXAMPLES  = ROOT_DIR / 'examples'

	unitest_args = ('-m', 'unittest', 'discover', '-s', str(ROOT_DIR))

	session.install('click') # For SBY
	session.install('.')

	if ENABLE_COVERAGE:
		session.log('Coverage support enabled')
		session.install('coverage')
		coverage_args = ('-m', 'coverage', 'run', '-p', f'--rcfile={ROOT_DIR / "pyproject.toml"}',)
		session.env['COVERAGE_CORE'] = 'sysmon'
	else:
		coverage_args = tuple[str]()

	with session.chdir(OUTPUT_DIR):
		session.log('Running core test suite...')
		session.run('python', *coverage_args, *unitest_args, *session.posargs)

		if SKIP_EXAMPLES:
			session.log('Skipping examples...')
		else:
			session.log('Testing examples...')
			with open(devnull, 'w') as f:
				for example in EXAMPLES.glob('**/*.py'):
					session.run('python', *coverage_args, str(example), 'generate', stdout = f)

		if ENABLE_COVERAGE:
			session.log('Combining Coverage data..')
			session.run('python', '-m', 'coverage', 'combine')

			session.log('Generating XML Coverage report...')
			session.run('python', '-m', 'coverage', 'xml', f'--rcfile={ROOT_DIR / "pyproject.toml"}')

@nox.session(name = 'watch-docs')
def watch_docs(session: Session) -> None:
	OUTPUT_DIR = BUILD_DIR / 'docs'

	session.install('-r', str(DOCS_DIR / 'requirements.txt'))
	session.install('sphinx-autobuild')
	session.install('.')

	session.run('sphinx-autobuild', str(DOCS_DIR), str(OUTPUT_DIR))

@nox.session(name = 'build-docs')
def build_docs(session: Session) -> None:
	OUTPUT_DIR = BUILD_DIR / 'docs'

	session.install('-r', str(DOCS_DIR / 'requirements.txt'))
	session.install('.')

	session.run('sphinx-build', '-b', 'html', str(DOCS_DIR), str(OUTPUT_DIR))

@nox.session(name = 'linkcheck-docs')
def linkcheck_docs(session: Session) -> None:
	OUTPUT_DIR = BUILD_DIR / 'docs-linkcheck'

	session.install('-r', str(DOCS_DIR / 'requirements.txt'))
	session.install('.')

	session.run('sphinx-build', '-b', 'linkcheck', str(DOCS_DIR), str(OUTPUT_DIR))

@nox.session(name = 'typecheck-mypy')
def typecheck_mypy(session: Session) -> None:
	OUTPUT_DIR = BUILD_DIR / 'typing' / 'mypy'
	OUTPUT_DIR.mkdir(parents = True, exist_ok = True)

	session.install('mypy')
	session.install('lxml')
	session.install('construct-typing')
	session.install('.')

	session.run(
		'mypy', '--non-interactive', '--install-types', '--pretty',
		'--cache-dir', str((OUTPUT_DIR / '.mypy-cache').resolve()),
		'-p', 'squishy', '--html-report', str(OUTPUT_DIR.resolve())
	)

@nox.session
def lint(session: Session) -> None:
	session.install('flake8')

	session.run(
		'flake8', '--config', str((CNTRB_DIR / '.flake8').resolve()),
		'./squishy', './tests', './examples', './docs'
	)

@nox.session
def dist(session: Session) -> None:
	session.install('build')

	session.run('python', '-m', 'build', '-o', str(DIST_DIR))
