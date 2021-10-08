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

_DEFAULT_GUI_SETTINGS = {
	'appearance': {
		'theme'          : 'system',
		'language'       : 'en_US',
		'font': {
			'name': 'Noto Sans',
			'size': 12,
		},

		'toolbar_style': 'icon_only',

		'hex_view': {
			'byte_format': 'hex',
			'font': {
				'name': 'Fira Code',
				'size': 12
			},

			'color_map': {
				'zero'     : '#494A50',
				'low'      : '#00994D',
				'high'     : '#CD427E',
				'ones'     : '#6C2DBE',
				'printable': '#FFB45B',
			}
		}
	},
	'capture': {

	},
	'device': {

	},
	'hotkeys': {

	}
}

class SquishyGui:
	def __init__(self):
		import json
		from os       import path
		from signal   import signal, SIGINT, SIG_DFL

		from ..config import SQUISHY_GUI_SETTINGS

		QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
		signal(SIGINT, SIG_DFL)

		if not path.exists(SQUISHY_GUI_SETTINGS):
			with open(SQUISHY_GUI_SETTINGS, 'w') as cfg:
				json.dump(_DEFAULT_GUI_SETTINGS, cfg)


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
