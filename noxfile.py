# SPDX-License-Identifier: BSD-3-Clause

import nox

nox.options.reuse_existing_virtualenvs = True

@nox.session
def tests(session: nox.Session) -> None:
	session.create_tmp()
	session.install('.')
	session.run(
		'python', '-m', 'unittest', 'discover',
		'-s', 'tests'
	)
