# SPDX-License-Identifier: BSD-3-Clause
import json

from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

from ..config          import SQUISHY_SETTINGS_FILE, DEFAULT_SETTINGS
from ..config          import BufferType, BufferBackend

from .resources        import *
from .widgets          import FontPicker, ColorPicker, HotkeyEdit
from .widgets.hex_view import ByteFormat

class PreferencesWindow:
	def _fill_appearance(self):
		appearance = self.settings['gui']['appearance']

		self.window.chk_splash.setChecked(appearance['show_splash'])
		self.window.fp_main.set_font(
			appearance['font']['name'],
			appearance['font']['size'],
		)

		self.window.cmb_hex_byte_style.setCurrentIndex(
			self.window.cmb_hex_byte_style.findText(
				appearance['hex_view']['byte_format']
			)
		)

		self.window.fp_hex.set_font(
			appearance['hex_view']['font']['name'],
			appearance['hex_view']['font']['size'],
		)
		self.window.clr_zero.set_color(
			appearance['hex_view']['color_map']['zero']
		)
		self.window.clr_low.set_color(
			appearance['hex_view']['color_map']['low']
		)
		self.window.clr_high.set_color(
			appearance['hex_view']['color_map']['high']
		)
		self.window.clr_max.set_color(
			appearance['hex_view']['color_map']['ones']
		)
		self.window.clr_printable.set_color(
			appearance['hex_view']['color_map']['printable']
		)

	def _fill_capture(self):
		capture = self.settings['capture']

		self.window.sb_capture_bsize.setValue(
			capture['buffer']['size']
		)

		self.window.cmb_cb_type.setCurrentIndex(
			self.window.cmb_cb_type.findText(
				capture['buffer']['type']
			)
		)

		self.window.cmb_cb_backend.setCurrentIndex(
			self.window.cmb_cb_backend.findText(
				capture['buffer']['backend']
			)
		)

	def _fill_device(self):
		device = self.settings['device']

	def _fill_hotkeys(self):
		hotkeys = self.settings['gui']['hotkeys']


	def _fill_settings(self):
		self._fill_appearance()
		self._fill_capture()
		self._fill_device()
		self._fill_hotkeys()


	def _save_appearance(self):
		appearance = self.settings['gui']['appearance']

		appearance['show_splash'] = self.window.chk_splash.checkState() == Qt.Checked
		appearance['font'] = {
			'name': self.window.fp_main._font_info.family(),
			'size': self.window.fp_main._font_info.pointSize(),
		}
		appearance['hex_view']['byte_format'] = str(self.window.cmb_hex_byte_style.currentData())
		appearance['hex_view']['font'] = {
			'name': self.window.fp_hex._font_info.family(),
			'size': self.window.fp_hex._font_info.pointSize(),
		}
		appearance['hex_view']['color_map'] = {
			'zero'     : self.window.clr_zero.color.name(),
			'low'      : self.window.clr_low.color.name(),
			'high'     : self.window.clr_high.color.name(),
			'ones'     : self.window.clr_max.color.name(),
			'printable': self.window.clr_printable.color.name(),
		}

	def _save_capture(self):
		capture = self.settings['capture']

		capture['buffer']['size'] = self.window.sb_capture_bsize.value()
		capture['buffer']['type'] = str(self.window.cmb_cb_type.currentData())
		capture['buffer']['backend'] = str(self.window.cmb_cb_backend.currentData())

	def _save_device(self):
		device = self.settings['device']

	def _save_hotkeys(self):
		hotkeys = self.settings['gui']['hotkeys']


	def _save_settings(self):
		self._save_appearance()
		self._save_capture()
		self._save_device()
		self._save_hotkeys()


		with open(SQUISHY_SETTINGS_FILE, 'w') as cfg:
			json.dump(self.settings, cfg)

		self.window.close()

	def _reset_settings(self):
		res = QMessageBox.question(
			self.window,
			'Reset Settings',
			'Would you really like to reset the settings to defaults?'
		)

		if res == QMessageBox.StandardButton.Yes:
			self.settings = DEFAULT_SETTINGS
			with open(SQUISHY_SETTINGS_FILE, 'w') as cfg:
				json.dump(self.settings, cfg)
			self._fill_settings()

	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			get_resource('preferences_window.ui', ResourceCategory.UI, ResourceType.PATH)
		)

		self.loader.registerCustomWidget(FontPicker)
		self.loader.registerCustomWidget(ColorPicker)
		self.loader.registerCustomWidget(HotkeyEdit)

		with open(SQUISHY_SETTINGS_FILE, 'r') as cfg:
			self.settings = json.load(cfg)

		self.window = self.loader.load(self._ui_file)

		self.window.btn_save.clicked.connect(self._save_settings)
		self.window.btn_reset.clicked.connect(self._reset_settings)
		self.window.lbl_settings.setText(f'Settings File: {SQUISHY_SETTINGS_FILE}')

		self.window.cmb_theme.addItems(QStyleFactory.keys())
		self.window.cmb_toolbar_style.addItems([
			'Icons Only',
			'Text Only',
			'Text and Icons',
		])

		for fmt in ByteFormat:
			self.window.cmb_hex_byte_style.addItem(str(fmt), userData = fmt)

		for typ in BufferType:
			self.window.cmb_cb_type.addItem(str(typ), userData = typ)

		for bck in BufferBackend:
			self.window.cmb_cb_backend.addItem(str(bck), userData = bck)

		self._fill_settings()

	def show(self):
		self.window.show()
