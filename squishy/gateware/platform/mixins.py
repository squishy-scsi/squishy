# SPDX-License-Identifier: BSD-3-Clause
import logging as log

from rich.progress import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn
)

from ...core.cache import SquishyBitstreamCache

__all__ = (
	'SquishyCacheMixin',
	'SquishyProgramMixin',
)

class SquishyProgramMixin:
	'''Squishy Platform programming mixin.

	This mixin overrides the :ref:`amaranth.build.plat.Platform` `toolchain_program` method
	to properly find and program Squishy boards.

	'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def toolchain_program(self, products, name, **kwargs):
		log.info('Programming')

class SquishyCacheMixin:
	'''Squishy Platform Cache mixin.

	This mixin overrides the :ref:`amaranth.build.plat.Platform` `build` method
	to inject FPGA bitstream caching via the :ref:`squishy.core.cache.SquishyBitstreamCache`
	which handles all bitstream and build caching based on the elaborated designs digest.

	This shortens build times, and removes the need to re-build unchanged applets.

	'''
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._cache = SquishyBitstreamCache()

	def build(self, elaboratable, name = 'top',
				build_dir = 'build', do_build = False,
				program_opts = None, do_program = False, **kwargs):

		skip_cache = kwargs.get('skip_cache', False)

		if skip_cache:
			log.warning('Skipping cache lookup, this might take a [yellow][i]while[/][/]', extra = { 'markup': True })

		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:
			task = progress.add_task('Elaborating Bitstream', start=False)

			plan = super().build(elaboratable, name,
					build_dir, do_build = False,
					program_opts = program_opts, do_program = False, **kwargs)

			if not do_build:
				return plan

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


			if not do_program:
				return prod

			progress.update(task, description = 'Programming Device')
			super().toolchain_program(prod, name, **(program_opts or {}))
