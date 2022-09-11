# SPDX-License-Identifier: BSD-3-Clause
import logging          as log
from pathlib            import Path
from typing             import Tuple
from collections        import OrderedDict


from rich.progress      import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn
)

from amaranth.build.run import LocalBuildProducts
from amaranth.hdl.ast   import SignalDict

from ...core.cache      import SquishyBitstreamCache

__all__ = (
	'SquishyCacheMixin',
	'SquishyProgramMixin',
)

__doc__ = '''\

The following are mixins that are used to add additional features to Amaranth platforms
without any extra setup work for the platform itself.

'''

class SquishyProgramMixin:
	'''Squishy Platform programming mixin.

	This mixin overrides the :py:class:`amaranth.build.plat.Platform` `toolchain_program` method
	to properly find and program Squishy boards.

	'''

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def toolchain_program(self, products, name: str, **kwargs):
		log.info('Programming')

class SquishyCacheMixin:
	'''Squishy Platform Cache mixin.

	This mixin overrides the :py:class:`amaranth.build.plat.Platform`. `build` method
	to inject FPGA bitstream caching via the :py:class:`squishy.core.cache.SquishyBitstreamCache`.
	which handles all bitstream and build caching based on the elaborated designs digest.

	This shortens build times, and removes the need to re-build unchanged applets.

	'''
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

		self._cache = SquishyBitstreamCache()

	def _build_slots(self) -> bytes:
		'''  '''
		from ..bootloader.bitstream import iCE40BitstreamSlots

		slot_data = bytearray(self.flash['geometry'].erase_size)
		slots     = iCE40BitstreamSlots(self.flash['geometry']).build()

		slot_data[0:len(slots)] = slots

		for byte in range(len(slots), self.flash['geometry'].erase_size):
			slot_data[byte] = 0xFF

		return bytes(slot_data)

	def _build_elaboratable(self, elaboratable, progress: Progress, name: str = 'top',
				build_dir: str = 'build', do_build: bool = False,
				program_opts: str = None, **kwargs):

		skip_cache = kwargs.get('skip_cache', False)

		if skip_cache:
			log.warning('Skipping cache lookup, this might take a [yellow][i]while[/][/]', extra = { 'markup': True })

		task = progress.add_task('Elaborating Bitstream', start=False)

		plan = super().build(elaboratable, name,
				build_dir, do_build = False,
				program_opts = program_opts, do_program = False, **kwargs)


		if not do_build:
			return (name, plan)

		digest = plan.digest(size = 32).hex()
		cache_obj = self._cache.get(digest)

		progress.update(task, description = 'Building Bitstream')

		if cache_obj is None or skip_cache:
			if not skip_cache:
				log.debug('Bitstream is not cached, building. This might take a [yellow][i]while[/][/]', extra = { 'markup': True })

			prod = plan.execute_local(build_dir)
			log.debug('Bitstream built')

			if not skip_cache:
				self._cache.store(digest, prod, name)
		else:
			name = cache_obj['name']
			prod = cache_obj['products']

			log.info(f'Using cached bitstream \'{name}\'')

		progress.remove_task(task)

		return (name, prod)

	def _build_multiboot(self, build_dir: str, name: str,
		boot: Tuple[str, LocalBuildProducts],
		applet: Tuple[str, LocalBuildProducts]) -> Path:

		build_path = Path(build_dir) / name

		boot_name   = boot[0]
		applet_name = applet[0]

		if not boot_name.endswith('.bin'):
			boot_name = boot_name + '.bin'

		if not applet_name.endswith('.bin'):
			applet_name = applet_name + '.bin'

		with build_path.open('wb') as multiboot:
			slot_data = self._build_slots()

			multiboot.write(slot_data)
			multiboot.write(boot[1].get(boot_name))

			start = multiboot.tell()
			end   = self.flash['geometry'].partitions[1]['start_addr']

			for _ in range(start, end):
				multiboot.write(b'\xFF')

			multiboot.write(applet[1].get(applet_name))


		return build_path


	def build(self, elaboratable, name: str = 'top',
				build_dir: str = 'build', do_build: bool = False,
				program_opts: str = None, do_program: bool = False, **kwargs):

		prod = LocalBuildProducts(build_dir)

		from ..bootloader.rev1 import Bootloader

		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:

			applet_name, applet_prod = self._build_elaboratable(elaboratable, progress, name, build_dir, do_build, program_opts, **kwargs)

			if not do_build:
				return applet_prod

			bootloader = Bootloader()

			self._requested = OrderedDict()
			self._phys_reqd = OrderedDict()
			self._conn_pins = OrderedDict()
			self._ports     = []
			self._clocks    = SignalDict()
			self._prepared = False
			boot_name, boot_prod = self._build_elaboratable(
				bootloader, progress, 'squishy_bootloader', build_dir, True, program_opts, **kwargs
			)

			final_bitstream = self._build_multiboot(build_dir, 'squishy-unified.bin', (boot_name, boot_prod), (applet_name, applet_prod))


			if not do_program:
				return prod

			programing_task = progress.add_task('Programming Device', start = False)
			super().toolchain_program(prod, final_bitstream.name, **(program_opts or {}))
			progress.update(programing_task, completed = True)
