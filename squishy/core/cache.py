# SPDX-License-Identifier: BSD-3-Clause

import logging       as log
from pathlib         import Path
from lzma            import LZMACompressor
from shutil          import rmtree
from typing          import (
	Union, Dict, List
)

from torii.build.run import LocalBuildProducts

from ..config        import SQUISHY_APPLET_CACHE

__all__ = (
	'SquishyBitstreamCache',
)

class SquishyBitstreamCache:
	''' Bitstream Cache system '''

	# Initialize the cache directory
	def _init_cache_dir(self, root: Path, depth: int = 1) -> None:
		if depth == 0:
			return

		for i in range(256):
			cache_stub = root / f'{i:02x}'
			if not cache_stub.exists():
				cache_stub.mkdir()
				self._init_cache_dir(cache_stub, depth - 1)

	def _decompose_digest(self, digest: str) -> List[str]:
		return [
			digest[
				(i*2):((i*2)+2)
			]
			for i in range(len(digest) // 2)
		]

	def _get_cache_dir(self, digest: str) -> Path:
		return self._cache_root.joinpath(
			*self._decompose_digest(digest)[
				:self.tree_depth
			]
		)

	def __init__(self, do_init: bool = True, tree_depth: int = 1, cache_rtl: bool = True) -> None:
		self.tree_depth  = tree_depth
		self.cache_rtl   = cache_rtl
		self._cache_root = Path(SQUISHY_APPLET_CACHE)

		if do_init:
			if not (self._cache_root / 'ca').exists():
				log.debug('Initializing bitstream cache tree')
				self._init_cache_dir(self._cache_root, tree_depth)

	def flush(self) -> None:
		''' Flush the cache '''
		log.info('Flushing applet cache')
		rmtree(self._cache_root)
		self._cache_root.mkdir()


	def get(self, digest: str) -> Dict[str, Union[str, LocalBuildProducts]]:
		'''Attempt to retrieve a bitstream based on it's elaboration digest'''
		bitstream_name = f'{digest}.bin'
		cache_dir = self._get_cache_dir(digest)
		bitstream = cache_dir / bitstream_name

		log.debug(f'Looking up bitstream \'{bitstream_name}\' in {cache_dir}')

		if not bitstream.exists():
			log.debug('Bitstream not found in cache')
			return None

		log.debug('Bitstream found')

		return {
			'name'    : bitstream_name,
			'products': LocalBuildProducts(str(cache_dir))
		}

	def store(self, digest: str, products: LocalBuildProducts, name: str) -> None:
		''' Store the synth products in the cache '''

		bitstream_name = f'{digest}.bin'
		cache_dir = self._get_cache_dir(digest)
		bitstream = cache_dir / bitstream_name

		log.debug(f'Caching bitstream \'{name}.bin\' in {cache_dir}')
		log.debug(f'New bitstream name: \'{bitstream_name}\'')

		with open(bitstream, 'wb') as bit:
			bit.write(products.get(f'{name}.bin'))

		if self.cache_rtl:
			rtl_name = f'{digest}.v.xz'
			rtl = cache_dir / rtl_name

			log.debug(f'Caching RTL \'{name}.debug.v\' in {cache_dir}')
			log.debug(f'New RTL name: \'{rtl_name}\'')

			cpr = LZMACompressor()

			with open(rtl, 'wb') as r:
				r.write(cpr.compress(products.get(f'{name}.debug.v')))
				r.write(cpr.flush())
