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

from PySide2.QtWidgets import QApplication
from PySide2.QtCore    import QCoreApplication, Qt
from ..gui             import MainWindow

class SquishyGui:
	def __init__(self):
		from os       import path
		from signal   import signal, SIGINT, SIG_DFL

		QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
		signal(SIGINT, SIG_DFL)


		self.app = QApplication.instance() or QApplication([])

		self.main_window = MainWindow()

	def run(self):
		self.main_window.show()
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
