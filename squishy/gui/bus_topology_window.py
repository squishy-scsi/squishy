# SPDX-License-Identifier: BSD-3-Clause
from os import path

from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

from .widgets          import BusTopologyWidget

class BusTopologyWindow:
	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			path.join(
				path.dirname(path.realpath(__file__)),
				'bus_topology_window.ui'
			)
		)

		self.loader.registerCustomWidget(BusTopologyWidget)

		self.window = self.loader.load(self._ui_file)


	def show(self):
		self.window.show()
