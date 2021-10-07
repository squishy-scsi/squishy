# SPDX-License-Identifier: BSD-3-Clause

ACTION_NAME = 'gui'
ACTION_DESC = 'Interactive SCSI gui'


def _check_pyside():
	try:
		import PySide6
		return True
	except:
		return False

if not _check_pyside():
	DONT_LOAD = 1




from PySide6.QtWidgets import QApplication
from PySide6.QtCore    import QCoreApplication, Qt
from ..gui             import MainWindow


class SquishyGui:
	def __init__(self):
		from os             import path
		from signal         import signal, SIGINT, SIG_DFL

		QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
		signal(SIGINT, SIG_DFL)

		self.app = QApplication.instance() or QApplication([])

		self.main_window        = MainWindow()



	def run(self):
		self.main_window.show()
		ret = self.app.exec()
		self.halt()
		return ret

	def halt(self):
		self.app.closeAllWindows()



def parser_init(parser):
	pass

def action_main(args):
	gui = SquishyGui()

	return gui.run()
