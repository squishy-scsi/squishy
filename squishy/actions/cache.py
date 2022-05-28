# SPDX-License-Identifier: BSD-3-Clause
import logging as log

from ..core.cache   import SquishyBitstreamCache
from ..config       import SQUISHY_CACHE, SQUISHY_APPLET_CACHE, SQUISHY_BUILD_DIR
from ..misc.utility import iec_size
from .              import SquishyAction

class Cache(SquishyAction):
	pretty_name  = 'Squishy Cache Utility'
	short_help   = 'Manage the Squishy cache'
	description  = 'Manages the Squishy cache'
	requires_dev = False

	def _list_cache(self, args):
		applet_size = 0
		build_size  = 0

		applet_items = list(SQUISHY_APPLET_CACHE.rglob('*.*'))
		build_items  = list(SQUISHY_BUILD_DIR.rglob('*.*'))

		for i in applet_items:
			applet_size += i.stat().st_size

		for i in build_items:
			build_size += i.stat().st_size

		total = applet_size + build_size

		log.info(f'Squishy applet cache contains {len(applet_items)} bitstream files totaling {iec_size(applet_size)}')
		log.info(f'Squishy build cache contains {len(build_items)} files totaling {iec_size(build_size)}')

		log.info(f'Total cache size is {iec_size(total)}')

		if args.list_cache_items:
			log.warning('Printing cache tree, as --list-cache-items was passed')
			log.warning('This might be very long')
			from rich.tree import Tree
			from rich      import print

			cache_tree = Tree(
				f'[green][link file://{str(SQUISHY_CACHE)}]{str(SQUISHY_CACHE)}[/][/]',
				guide_style = 'blue'
			)

			applet_tree = cache_tree.add('[bright_red]applets[/]')

			segments = dict()

			for item in applet_items:
				s = str(item.parent).split("/")[-1]
				if s not in segments:
					segments[s] = applet_tree.add(f'[magenta]{s}[/]')
				segments[s].add(f'{item.name}')

			build_tree = cache_tree.add('[bright_red]build[/]')

			for item in build_items:
				build_tree.add(f'{item.name}')

			print(cache_tree)

	def _clear_cache(self, args):
		from rich.prompt import Confirm
		from shutil      import rmtree

		if Confirm.ask('Are you sure you want to clear the cache?'):
			bc = SquishyBitstreamCache(False)
			bc.flush()
			log.info('Flushing build cache')
			rmtree(SQUISHY_BUILD_DIR)
			SQUISHY_BUILD_DIR.mkdir()
			return 0
		else:
			log.info('Aborted')
			return 1

	def __init__(self):
		super().__init__()

		self._dispatch = {
			'list': self._list_cache,
			'clear': self._clear_cache,
		}

	def register_args(self, parser):
		actions = parser.add_subparsers(
			dest     = 'cache_action',
			required = True
		)

		cache_list = actions.add_parser(
			'list',
			help = 'list cache contents and size'
		)

		cache_list.add_argument(
			'--list-cache-items',
			action = 'store_true',
			help   = 'List each item in the cache (WARNING, THIS CAN BE LARGE)'
		)

		cache_clear = actions.add_parser( # noqa: F841
			'clear',
			help = 'clear cache'
		)

	def run(self, args, dev = None):
		return self._dispatch.get(args.cache_action, lambda _: 1)(args)
