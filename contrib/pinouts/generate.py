#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause

import json
from pathlib import Path
from typing  import TypedDict, Literal

from pinout.core                  import Group, Image, StyleSheet
from pinout.components.layout     import Diagram, Diagram_2Rows, Panel
from pinout.components.pinlabel   import PinLabelGroup
from pinout.components.annotation import AnnotationLabel
from pinout.components.text       import TextBlock
from pinout.components            import leaderline
from pinout.components.legend     import Legend

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_DIR           = (SCRIPT_DIR / 'data')
CONNECTOR_DIR      = (DATA_DIR / 'connectors')
CONNECTOR_METADATA = (CONNECTOR_DIR / 'metadata.json')
CSS_FILE           = (DATA_DIR / 'pinout.css').resolve()
IMG_DIR            = (SCRIPT_DIR.parent / 'img')

LegendDef = TypedDict('LegendDef', {'class': str, 'title': str})
PinDef    = TypedDict('PinDef', {'class': str, 'name': str})

class PinoutDef(TypedDict):
	title: str
	description: str
	legend: list[LegendDef]
	connectors: list[str]
	pinout: dict[str, PinDef]

class LabelsDef(TypedDict):
	start: int
	pitch: int

class PositionDef(TypedDict):
	x: int
	y: int

class ConnectorDef(TypedDict):
	image: str
	name: str
	width: int
	height: int
	pitch: int
	order: Literal['odd-even'] | Literal['top-bottom']
	labels: LabelsDef
	pin_map: dict[str, PositionDef]

NormalizedDef = list[list[tuple[int | str, str]]]

def generate_mapping_top_bottom(conductors: int) -> dict[int, int]:
	topBottomPinning = [f'{pinTopBottom + 1}' for pinTopBottom in range(conductors)]
	# if doing an anti-clockwise mapping the second list in the tuple needs to be .reversed()'d
	topBottomPinning = (topBottomPinning[:conductors // 2], topBottomPinning[conductors // 2:])

	oddEvenPinning = { f'{pinOddEven + 1}': topBottomPinning[pinOddEven % 2][pinOddEven >> 1] for pinOddEven in range(conductors)}
	return oddEvenPinning


def normalize_pins(connector_def: dict[str, PinDef], pin_order: str) -> tuple[NormalizedDef, NormalizedDef]:

	if pin_order == 'odd-even':
		pindefs_l = list(filter(lambda i: int(i[0], 10) % 2 != 0, connector_def.items()))
		pindefs_r = list(filter(lambda i: int(i[0], 10) % 2 == 0, connector_def.items()))
	elif pin_order == 'top-bottom':
		# Generate the odd-even to top-bottom translation map
		MAPPING = generate_mapping_top_bottom(len(connector_def))

		_items = list(map(lambda itm: (MAPPING[itm[0]], itm[1]), connector_def.items()))
		_items.sort(key = lambda k: int(k[0], 10))
		_per_side = len(_items) // 2
		pindefs_l = _items[:_per_side]
		pindefs_r = _items[_per_side:]
	else:
		raise NotImplementedError(f'Normalization for pin mapping of \'{pin_order}\' is not implemented')

	def _normalize(pin_defs: list[tuple[str, PinDef]]) -> NormalizedDef:
		pins = []
		for pdef in pin_defs:
			num, info = pdef[0], pdef[1]
			pin_def = []

			pin_def.append(
				(int(num, 10), 'pin')
			)
			pin_def.append(
				(info['name'], info['class'])
			)

			pins.append(pin_def)
		return pins

	return _normalize(pindefs_l), _normalize(pindefs_r)

def mk_legend(legend: LegendDef) -> list[tuple[str, str]]:
	legend_entries = []

	for entry in legend:
		legend_entries.append(
			(entry['title'], entry['class'])
		)

	return legend_entries

def mk_diagram(
	conn_name: str, conn_info: ConnectorDef, legend: list[tuple[str, str]],
	conn_left: NormalizedDef, conn_right: NormalizedDef, title: str, desc: str
) -> Diagram:
	CONNECTOR_FILE = (CONNECTOR_DIR / f'{conn_info["image"]}').resolve()
	GUTTER_HEIGHT  = 200

	conn_pitch  = conn_info['pitch']
	conn_height = conn_info['height']
	conn_width  = conn_info['width']
	label_info  = conn_info['labels']
	conn_order  = conn_info['order']

	diagram = Diagram_2Rows(800, conn_height + GUTTER_HEIGHT, conn_height + 45, 'diagram')
	diagram.add_stylesheet(CSS_FILE, embed = True)

	graphic = diagram.panel_01.add(Group(320, 20))

	hw = graphic.add(Image(CONNECTOR_FILE, embed = True, width = conn_width, height = conn_height))

	pin_count = len(conn_info['pin_map'].items())

	for pin_num, coords in conn_info['pin_map'].items():
		hw.add_coord(pin_num, x = coords['x'], y = coords['y'])

	hw.add_coord('pin_pitch', x = 0, y = conn_pitch)

	if conn_order == 'odd-even':
		hwc_left = hw.coord('1')
		hwc_right = hw.coord('2')
	elif conn_order == 'top-bottom':
		hwc_left = hw.coord('1')
		hwc_right = hw.coord(f'{(pin_count // 2) + 1}')


	graphic.add(PinLabelGroup(
		x = hwc_left.x,
		y = hwc_left.y,
		pin_pitch = hw.coord('pin_pitch', raw = True),
		label_start = (label_info['start'], 0),
		label_pitch = (0, label_info['pitch']),
		scale = (-1, 1),
		labels = conn_left
	))

	graphic.add(PinLabelGroup(
		x = hwc_right.x,
		y = hwc_right.y,
		pin_pitch = hw.coord('pin_pitch', raw = True),
		label_start = (label_info['start'], 0),
		label_pitch = (0, label_info['pitch']),
		labels = conn_right
	))

	# Add Title
	title_blk = diagram.panel_02.add(TextBlock(
		f'<tspan class="h1">{title} ({conn_name.upper()})</tspan>',
		x = 20,
		y = 30,
		line_height = 18,
		tag = 'panel title_block'
	))

	# Add Description
	diagram.panel_02.add(TextBlock(
		desc,
		x = 20,
		y = 60,
		width = title_blk.width,
		height = diagram.panel_02.height - title_blk.height,
		line_height = 18,
		tag = 'panel text_block'
	))

	# Add Legend
	diagram.panel_02.add(Legend(
		legend,
		x = 630,
		y = 8,
		max_height = 230
	))

	return diagram


def resolve_embeds(diagram: Diagram):
	imgs = diagram.find_children_by_type(diagram, Image)

	for img in imgs:
		while isinstance(img.src, Image):
			img = img.src

		#  if not img.embed and not img.src.is_absolute():
		# 	img.src = Path.cwd() / Path(img.src)

	# stylesheets = diagram.find_children_by_type(diagram, StyleSheet)
	# for css in stylesheets:
	#

def render_pinout(pinout_file: Path, conn_meta: dict[str, ConnectorDef]):
	print(f'Reading pinout file: {pinout_file.name}')
	with pinout_file.open('r') as f:
		pinout_def: PinoutDef = json.load(f)

	legend = mk_legend(pinout_def['legend'])



	title = pinout_def['title']
	desc  = pinout_def['description']

	for conn in pinout_def['connectors']:
		conn_info = conn_meta.get(conn)
		if conn_info is None:
			print(f'WARN: No connector info for {conn}! Skipping')
			continue

		conn_left, conn_right = normalize_pins(pinout_def['pinout'], conn_info['order'])
		diagram = mk_diagram(conn, conn_info, legend, conn_left, conn_right, title, desc)

		resolve_embeds(diagram)

		output_file = (IMG_DIR / f'{pinout_file.stem}-{conn}.svg')
		output_file.write_text(diagram.render())



if __name__ == '__main__':
	with CONNECTOR_METADATA.open('r') as f:
		conn_meta: dict[str, ConnectorDef] = json.load(f)

	for pinout_file in DATA_DIR.glob('*.json'):
		# try:
		render_pinout(pinout_file, conn_meta)
		# except Exception as e:
		# 	print(f'Failed to render pinout for {pinout_file.name}: {e}')
