# SPDX-License-Identifier: BSD-3-Clause

'''

'''

import logging           as log
from io                  import BytesIO
from tarfile             import open as tf_open
from tarfile             import TarInfo

from torii.build.run     import BuildPlan, BuildProducts, LocalBuildProducts

from ..paths             import SQUISHY_ASSET_CACHE
from ..gateware.platform import SquishyPlatformType

__all__ = (
	'SquishyCache',
)

class SquishyCache:
	'''
	Squishy on-disk bitstream cache.

	'''

	ARCHIVE_ASSETS = (
		# Synthesis Input
		'debug.v', 'il', 'ys',
		# PnR Output
		'tim', 'tim.json', 'pnr.json',
	)

	def __init__(self) -> None:
		self._cache_root = SQUISHY_ASSET_CACHE

	def get(self, plan: BuildPlan) -> BuildProducts | None:
		'''
		Get the cached version of the built gateware

		Parameters
		----------
		plan : BuildPlan
			The generated build plan from Torii.

		Returns
		-------
		BuildProducts | None
			If found in the cache, an instance of LocalBuildProducts, otherwise None

		'''

		plan_digest = plan.digest(size = 32).hex()
		cache_dir   = self._cache_root / plan_digest[0:2] / plan_digest

		if not cache_dir.exists():
			return None

		log.debug(f'Found cache entry \'{plan_digest}\'')

		return LocalBuildProducts(cache_dir)

	def store(self, name: str, products: BuildProducts, plan: BuildPlan, plat: SquishyPlatformType) -> BuildProducts:
		'''
		Store the gateware, generated HDL, and synthesis/pnr logs in the cache.

		Parameters
		----------
		name : str
			The name of the gateware.

		products : BuildProducts
			The output BuildProducts from executing the Torii BuildPlan.

		products : BuildPlan
			The plan that was used to produce `products`

		plat : SquishyPlatformType
			The platform that we built against

		Returns
		-------
		BuildProducts
			The re-homed BuildProducts from the cache rather than the build directory.

		'''

		plan_digest = plan.digest(size = 32).hex()
		cache_dir   = self._cache_root / plan_digest[0:2] / plan_digest

		log.debug(f'Caching build assets for \'{name}\'')
		log.debug(f'Cache path: \'{cache_dir}\'')

		if cache_dir.exists():
			log.warning(f'Cache collision on asset entry \'{plan_digest}\'')
			for item in cache_dir.iterdir():
				item.unlink()
		else:
			log.debug('No cache entry found, creating')
			cache_dir.mkdir(parents = True)


		# Archive build assets
		arc_name = f'{name}.src.tar.xz'
		arc_path = cache_dir / arc_name

		log.debug(f'Archiving build assets to cache in \'{arc_name}\'')

		with tf_open(arc_path, 'w:xz') as arc:
			for asset in self.ARCHIVE_ASSETS:
				f_name = f'{name}.{asset}'
				try:
					data = products.get(f_name, 'b')

					log.debug(f' => \'{f_name}\'')

					info = TarInfo(f_name)
					info.size   = len(data)

					arc.addfile(info, BytesIO(data))
				except OSError:
					continue

		# Copy the timing/utilization report out before we re-home
		log.debug('Caching PnR Utilization report outside of asset archive')
		with (cache_dir / f'{name}.tim.json').open('wb') as bitstream:
			bitstream.write(products.get(f'{name}.tim.json', 'b'))

		# Cache the bitstream
		log.debug('Caching bitstream')
		f_name = f'{name}.{plat.bitstream_suffix}'
		with (cache_dir / f_name).open('wb') as bitstream:
			bitstream.write(products.get(f_name, 'b'))

		return LocalBuildProducts(cache_dir)
