# SPDX-License-Identifier: BSD-3-Clause
import logging as log

from ...cache import SquishyBitstreamCache

__all__ = (
	'SquishyCacheMixin',
)


class SquishyCacheMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._cache = SquishyBitstreamCache()

	def build(self, elab, name = 'top',
				build_dir = 'build', do_build = False,
				program_opts = None, do_program = False, **kwargs):

		plan = super().build(elab, name,
				build_dir, do_build = False,
				program_opts = program_opts, do_program = False, **kwargs)

		if not do_build:
			return plan

		if not kwargs.get('skip_cache', False):
			digest = plan.digest(size = 32).hex()
			cache_obj = self._cache.get(digest)

			if cache_obj is None:
				log.debug(f'Bitstream is not cached, building')
				prod = plan.execute_local(build_dir)
				self._cache.store(digest, prod, name)
			else:
				name = cache_obj['name']
				prod = cache_obj['products']
		else:
			log.info('Skipping cache lookup')
			prod = plan.execute_local(build_dir)

		if not do_program:
			return prod

		super().toolchain_program(prod, name, **(program_opts or {}))