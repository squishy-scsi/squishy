# SPDX-License-Identifier: BSD-3-Clause
from .. import __version__

ACTION_NAME = 'gui'
ACTION_DESC = 'Interactive SCSI gui'

def _check_pyside():
	try:
		import PySide2
		return True
	except:
		return False

if not _check_pyside():
	DONT_LOAD = 1

from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui     import QPixmap, QIcon
from PySide2.QtCore    import QCoreApplication, Qt

from ..config          import SQUISHY_SETTINGS_FILE
from ..gui             import MainWindow
from ..gui.resources   import *

class SquishyGui:
	def __init__(self):
		import json
		from os     import path
		from signal import signal, SIGINT, SIG_DFL

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

		self.main_window = MainWindow(self.settings)

	def run(self):
		self.main_window.show()
		if self.settings['gui']['appearance']['show_splash']:
			self.splash.finish(self.main_window.window)
		ret = self.app.exec_()
		# self.halt()
		return ret

	def halt(self):
		self.app.closeAllWindows()



def parser_init(parser):
	pass

def action_main(args):
	gui = SquishyGui()
	banner = fr'''
------------------------------------------
 ####   ####  #    # #  ####  #    # #   #
#      #    # #    # # #      #    #  # #
 ####  #    # #    # #  ####  ######   #
     # #  # # #    # #      # #    #   #
#    # #   #  #    # # #    # #    #   #
 ####   ### #  ####  #  ####  #    #   #
------------------------------------------
################ QT5 GUI #################
------------------------------------------
squishy version: {__version__}
'''

	print(banner, end = '')

	return gui.run()
