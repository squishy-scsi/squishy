# SPDX-License-Identifier: BSD-3-Clause

import json
from pathlib              import Path
from signal               import signal, SIGINT, SIG_DFL

from PySide2.QtWidgets    import QApplication, QSplashScreen
from PySide2.QtGui        import QPixmap, QIcon
from PySide2.QtCore       import QCoreApplication, Qt

from ..config             import SQUISHY_SETTINGS_FILE
from ..core.collect       import collect_members, predicate_action

from .resources           import *

from .windows             import MainWindow

class SquishyGui:
	def __init__(self):
		QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
		signal(SIGINT, SIG_DFL)

		# load settings
		with open(SQUISHY_SETTINGS_FILE, 'r') as cfg:
			self.settings = json.load(cfg)

		self.app = QApplication.instance() or QApplication([])

		# Ensure we can find our themes/resources
		QIcon.setThemeSearchPaths([
			':/icons',
		])

		if self.settings['gui']['appearance']['show_splash']:
			self.splash = QSplashScreen(
				QPixmap(get_resource('splash.png', ResourceCategory.IMAGE, ResourceType.PATH))
			)
			self.splash.show()

		from .. import actions
		self._ACTIONS = collect_members(
			Path(actions.__path__[0]),
			predicate_action,
			f'{actions.__name__}.'
		)

		self.main_window = MainWindow(self.settings)

	def register_args(self, parser):
		pass

	def run(self, args = None):
		self.main_window.show()
		if self.settings['gui']['appearance']['show_splash']:
			self.splash.finish(self.main_window.window)
		ret = self.app.exec_()
		# self.halt()
		return ret

	def halt(self):
		self.app.closeAllWindows()
