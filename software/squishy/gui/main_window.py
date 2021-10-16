# SPDX-License-Identifier: BSD-3-Clause
from os                   import path
from random               import choice

from PySide2.QtCore       import *
from PySide2.QtWidgets    import *
from PySide2.QtUiTools    import QUiLoader

from ..config             import SQUISHY_SPLASH_MESSAGES

from .widgets             import HexViewWidget, CaptureLog
from .about_window        import AboutWindow
from .bus_topology_window import BusTopologyWindow
from .devices_window      import DevicesWindow
from .filters_window      import FiltersWindow
from .preferences_window  import PreferencesWindow
from .triggers_window     import TriggersWindow

class MainWindow:
	def _populate_settings(self):
		pass

	def __init__(self, settings):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			path.join(
				path.dirname(path.realpath(__file__)),
				'main_window.ui'
			)
		)

		self._settings = settings

		self.loader.registerCustomWidget(CaptureLog)
		self.loader.registerCustomWidget(HexViewWidget)

		self.window = self.loader.load(self._ui_file)

		self.about_window       = AboutWindow()
		self.bus_window         = BusTopologyWindow()
		self.devices_window     = DevicesWindow()
		self.filters_window     = FiltersWindow()
		self.preferences_window = PreferencesWindow()
		self.triggers_window    = TriggersWindow()

		# Window View Events
		self.window.action_help_about.triggered.connect(lambda _: self.about_window.show())
		self.window.action_view_bus_topology.triggered.connect(lambda _: self.bus_window.show())
		self.window.action_edit_preferences.triggered.connect(lambda _: self.preferences_window.show())
		self.window.action_capture_filters.triggered.connect(lambda _: self.filters_window.show())
		self.window.action_capture_triggers.triggered.connect(lambda _: self.triggers_window.show())
		self.window.action_capture_select_device.triggered.connect(lambda _: self.devices_window.show())

		# File IO
		self.window.action_file_open.triggered.connect(self.open_file)
		self.window.action_file_save.triggered.connect(self.save_file)


		self._populate_settings()


	def open_file(self, _):
		file = QFileDialog.getOpenFileName(
				self.window,
				'Open Capture',
				path.expanduser('~'),
				'Packet Captures (*.pcapng, *.pcapng.gz)'
			)

	def save_file(self, _):
		file = QFileDialog.getSaveFileName(
				self.window,
				'Save Capture',
				path.expanduser('~'),
				'Packet Captures (*.pcapng, *.pcapng.gz)'
			)

	def show(self):
		self.window.show()
		self.window.statusbar.showMessage(choice(SQUISHY_SPLASH_MESSAGES), 10e4)
