# SPDX-License-Identifier: BSD-3-Clause

'''
The Squishy CLI (and to some extent, the eventual REPL), consists mainly of invoking actions.

Currently there are the following actions:
* :py:mod:`squishy.actions.applet` - Everything to do with building and running Squishy Applets.
* :py:mod:`squishy.actions.provision` - Used for producing device images for hardware.

There are two primary types of actions, the first is the :py:class:`SquishyAction`, this is the
progenitor for every action within Squishy, it defines the needed properties and public interface
used to invoke the action.

The second of the two is the :py:class:`SquishySynthAction`, this has extra specialization for any
Squishy actions that involve synthesizing gateware for the Squishy hardware. It is superset of
:py:class:`SquishyAction` and abstracts all of the synthesis, pnr, and packing options and machinery
away.

'''

import logging       as log
import json

from abc             import ABCMeta, abstractmethod
from argparse        import ArgumentParser, Namespace
from pathlib         import Path
from subprocess      import CalledProcessError

from rich.progress   import Progress, SpinnerColumn, BarColumn, TextColumn

from torii           import Elaboratable
from torii.build.run import BuildPlan, LocalBuildProducts

from ..device        import SquishyDevice
from ..core.config   import USB_VID, USB_APP_PID, USB_DFU_PID
from ..core.cache    import SquishyCache
from ..gateware      import AVAILABLE_PLATFORMS, SquishyPlatformType

__all__ = (
	'SquishyAction',
	'SquishySynthAction',
)

class SquishyAction(metaclass = ABCMeta):
	'''
	Base class for all invocable actions from the Squishy CLI.

	This defines a common interface that the main CLI, or any other
	consumer of Squishy can use to reliably invoke actions.

	Attributes
	----------
	name : str
		The name used to invoke the action and display in the help documentation.

	description : str
		A short description of what this action does, used in the help.

	requires_dev : bool
		Whether or not this action requires physical Squishy hardware.

	Note
	----
	Actions should be sure to also overload the doc comments when derived
	as to allow for :py:class:`HelpAction` to generate appropriate long-form
	documentation when invoked.

	'''

	@property
	@abstractmethod
	def name(self) -> str:
		''' The name of the action. '''
		raise NotImplementedError('Actions must implement this property')

	@property
	@abstractmethod
	def description(self) -> str:
		''' Short description of the action. '''
		raise NotImplementedError('Actions must implement this property')

	@property
	@abstractmethod
	def requires_dev(self) -> bool:
		''' Whether or not this action requires a physical hardware device. '''
		raise NotImplementedError('Actions must implement this property')

	def __init__(self) -> None:
		pass

	@abstractmethod
	def register_args(self, parser: ArgumentParser) -> None:
		'''
		Register action argument parsers.

		After initialization, but prior to being invoked with :py:func:`.run`
		this method will be called to allow the action to register any wanted
		command line options.

		This is also used when displaying help.

		Parameters
		----------
		parser : argparse.ArgumentParser
			The Squishy CLI argument parser group to register arguments into.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.

		'''
		raise NotImplementedError('Actions must implement this method')

	@abstractmethod
	def run(self, args: Namespace, dev: SquishyDevice | None = None) -> int:
		'''
		Invoke the action.

		This method is run when the Squishy CLI has determined that this action
		was to be called.

		Parameters
		----------
		args : argsparse.Namespace
			The parsed arguments from the Squishy CLI

		dev : squishy.device.SquishyDevice | None
			The device this action was invoked on if any.

		Returns
		-------
		int
			0 if run was successful, otherwise an error code.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.

		'''
		raise NotImplementedError('Actions must implement this method')

class SquishySynthAction(SquishyAction):
	'''
	Common base class derived from :py:`SquishyAction` for all Squishy CLI
	actions that synthesize gateware.

	This lets us abstract away needed common command line argument setup and
	parsing, and having all the needed machinery for it be self-contained.

	There are three additional methods that this provides that are for use
	by synthesis based actions.

	The first is :py:meth:`.get_platform`, this will return the appropriate
	:py:class:`squishy.gateware.SquishyPlatform` for the given hardware device
	that is attached, or ``None`` if it's not able to determine the platform or
	a device is not attached

	The next is :py:meth:`.register_synth_args`, this provides the registration
	mechanism to populate the action with all relevant command line arguments
	related to the synthesis of the gateware for the target device.

	Finally there is :py:meth:`.run_synth` which does the actual invocation of
	the synthesis run.

	'''

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self._cache = SquishyCache()

	def get_platform(self, args: Namespace, dev: SquishyDevice | None) -> type[SquishyPlatformType] | None:
		'''
		Get the platform to synthesize for, either from the selected device or the `--platform` cli option.

		Parameters
		----------
		args : argsparse.Namespace
			The parsed arguments from the action invocation.

		dev : SquishyDevice | None
			The optional device to extract the platform from

		Returns
		-------
		SquishyPlatformType | None
			The extracted platform if possible, otherwise None
		'''

		# TODO(aki): If we are in `--build-only` mode, should we override the resulting platform if we *do* have a dev?
		#            This means we need to change `--platform` so it doesn't have a default.

		# If we were passed a device, pull the platform from that
		if dev is not None:
			plat = dev.get_platform()
			if plat is None:
				log.error(f'Attempted to get platform for device {dev.serial}, but failed?')
		# Otherwise, get it the long way
		else:
			plat = AVAILABLE_PLATFORMS.get(args.platform, None)
			if plat is None:
				log.error(f'Unknown platform {args.platform}')

		return plat

	def run_synth(
			self, args: Namespace, platform: SquishyPlatformType, elaboratable: Elaboratable,
			name: str, build_dir: Path, cacheable: bool = True, *, pnr_seed: int | None = None
	) -> LocalBuildProducts | None:
		'''
		Run gateware synthesis, place-and-route, and bitstream packing in a cache-aware manner.

		Parameters
		----------
		args : argsparse.Namespace
			The parsed arguments from the action invocation.

		platform : SquishyPlatformType
			The target Squishy platform we are synthesizing for.

		elaboratable : torii.Elaboratable
			The root/'top' gateware module to synthesize.

		name : str
			The root/'top' gateware module name.

		build_dir : Path
			The requested build directory, is overridden by the `--build-dir` cli option

		cacheable : bool
			Whether or not to process cache-related options. Default: True

		pnr_seed : int | None
			The new default PNR seed to use if supplied, still overloaded by `--pnr-seed`.

		Returns
		-------
		LocalBuildProducts
			The resulting built artifacts upon successful build

		None
			On a failed build there are no resulting products
		'''

		synth_opts: list[str] = []
		pnr_opts: list[str] = []
		pack_opts: list[str] = []

		script_pre_synth = ''
		script_post_synth = ''


		if not build_dir.exists():
			log.debug(f'Creating build directory {build_dir}')
			build_dir.mkdir(parents = True)

		# By default skip cache
		skip_cache = not cacheable
		if cacheable:
			skip_cache: bool = args.skip_cache

		# Synthesis Options
		if not args.no_abc9:
			synth_opts.append('-abc9')

		if not args.no_aggressive_mapping:
			if args.no_abc9:
				log.warning('option `--no_aggressive_mapping` passed along with `--no-abc9`, ignoring')
			else:
				script_pre_synth += 'scratchpad -copy abc9.script.flow3 abc9.script\n'

		# Place-and-Route Options
		pnr_opts.append(f'--report {name}.tim.json')
		if args.detailed_report:
			pnr_opts.append('--detailed-timing-report')

		if not args.no_routed_netlist:
			pnr_opts.append(f'--write {name}.pnr.json')


		# Check to see if we're overloading the default PNR seed, and said seed is the default
		if pnr_seed is not None and args.pnr_seed == 0:
			pnr_opts.append(f'--seed {pnr_seed}')
		elif args.pnr_seed < 0:
			# If the seed is negative, use a random seed
			pnr_opts.append('-r')
		else:
			pnr_opts.append(f'--seed {args.pnr_seed}')


		# Packing Options
		if not args.dont_compress:
			pack_opts.append('--compress')

		if args.lie:
			match platform.device[-3:]:
				case '25F':
					pack_opts.append('--idcode 0x01111043')
				case '45F':
					pack_opts.append('--idcode 0x01112043')
				case '85F':
					pack_opts.append('--idcode 0x01113043')

		log.info(f'Using platform version: {platform.revision_str}')
		log.info(f'    Device: {platform.device}-{platform.package}')
		if args.lie:
			log.warning('Packing for non-5G device, you\'re on your own, good luck')

		# Run the synth, pnr, et. al.
		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:
			# First we run a `prepare` which will do RTL generation

			task = progress.add_task('Elaborating Bitstream', start = False)

			plan: BuildPlan = platform.prepare(
				elaboratable,
				name               = name,
				build_dir          = build_dir,
				synth_opts         = synth_opts,
				nextpnr_opts       = pnr_opts,
				ecppack_opts       = pack_opts,
				verbose            = args.build_verbose,
				debug_verilog      = cacheable and not skip_cache,
				script_after_read  = script_pre_synth,
				script_after_synth = script_post_synth
			)

			# If we are not skipping the cache, try to get the built result
			prod = None
			if not skip_cache:
				prod = self._cache.get(plan)

			# Run the build
			if prod is None:
				log.info('Bitstream is not cached, this might take [yellow][i]a while[/][/]', extra = { 'markup': True })
				progress.update(task, description = 'Building bitstream')
				try:
					prod = plan.execute_local(build_dir)
				except CalledProcessError:
					# TODO(aki): Should we copy the files out from the build directory into somewhere like '/tmp'
					#            and point users to that rather than make them reach into the cache dir?
					log.error(f'Building bitstream for \'{name}\' failed')
					log.error(f'Consult the following log files in {build_dir} for more details:')
					log.error(f'  [cyan]*[/] [link={build_dir}/{name}.rpt]\'{name}.rpt\'[/] [dim](Synthesis Report)[/]', extra = { 'markup': True })
					log.error(f'  [cyan]*[/] [link={build_dir}/{name}.tim]\'{name}.tim\'[/] [dim](PnR Report)[/]', extra = { 'markup': True })
					return None

				# If we're allowed to, cache the products and then return that cached version
				if not skip_cache:
					log.info('Caching built bitstream')
					progress.update(task, description = 'Caching build')
					prod = self._cache.store(name, prod, plan, platform)
			else:
				log.info('Found built gateware in cache, using that')

			progress.remove_task(task)
		# If we're in verbose logging mode, go the extra step and print out the utilization report
		if args.verbose:
			self.dump_utilization(name, prod)

		return prod


	def register_synth_args(self, parser: ArgumentParser, cacheable: bool = True) -> None:
		'''
		Register common Synthesis, Place and Route, and Bitstream packing options.

		Parameters
		----------
		parser : argsparse.ArgumentParser
			The root action argument parser to register the options into.

		cacheable : bool
			Whether or not to show cache-related options. Default: True
		'''

		parser.add_argument(
			'--platform', '-p',
			type    = str,
			default = list(AVAILABLE_PLATFORMS.keys())[-1], # Always pick the latest platform as the default
			choices = list(AVAILABLE_PLATFORMS.keys()),
			help    = 'The target hardware platform to synthesize for.'
		)

		generic_options = parser.add_argument_group('Generic Options')

		# TODO(aki): Should this be the default w/ needing to pass `--program` to program instead?
		generic_options.add_argument(
			'--build-only', '-B',
			action = 'store_true',
			help   = 'Only build and pack the gateware, skip device programming.'
		)

		generic_options.add_argument(
			'--build-dir', '-b',
			type    = Path,
			help    = 'The output directory for the intermediate and final build artifacts.'
		)

		if cacheable:
			generic_options.add_argument(
				'--skip-cache', '-C',
				action = 'store_true',
				help   = 'Skip artifact cache lookup, and don\'t cache the resulting gateware artifact once built.'
			)

		# TODO(aki): Should this be rather tied into `-v`, and if we pass 2 it flips this switch?
		generic_options.add_argument(
			'--build-verbose',
			action = 'store_true',
			help   = 'Enable verbose output during build (very noisy)'
		)

		synth_options = parser.add_argument_group('Synthesis Options')

		synth_options.add_argument(
			'--no-abc9',
			action = 'store_true',
			help   = 'Disable the use of `abc9` during synth.'
		)

		synth_options.add_argument(
			'--no-aggressive-mapping',
			action = 'store_true',
			help   = 'Disable multiple `abc9` mapping passes, resulting in faster synth time but worse overall gateware performance.'
		)

		pnr_options = parser.add_argument_group('Place-and-Route Options')

		pnr_options.add_argument(
			'--detailed-report',
			action = 'store_true',
			help   = 'Have nextpnr output a detailed timing report'
		)

		pnr_options.add_argument(
			'--no-routed-netlist',
			action = 'store_true',
			help   = 'Don\'t write out the netlist with embedded routing information for later inspection.'
		)

		pnr_options.add_argument(
			'--pnr-seed',
			type    = int,
			default = 0,
			help    = 'The place and route RNG seed to use.'
		)

		pack_options = parser.add_argument_group('Bitstream Packing Options')

		pack_options.add_argument(
			'--dont-compress',
			action  = 'store_true',
			help    = 'Disable bitstream compression if viable for target platform.'
		)

		pack_options.add_argument(
			'--lie',
			action = 'store_true',
			help   = 'Lie about our device ID, telling the packing tool to emit a bitstream for the non 5G version'
		)

	def dfu_util_msg(self, name: str, slot: int, build_dir: Path, dev: SquishyDevice | None = None) -> str:
		'''
		Build up a message that accurately displays how to flash a built artifact to the given Squishy device.

		Parameters
		----------
		name : str
			The name of the artifact that was generated.

		slot : int
			The DFU slot/alt-mode to specify.

		build_dir : Path
			The gateware build directory that was used

		dev : SquishyDevice | None
			If attached, a Squishy device to pull the serial number from

		Returns
		-------
		str
			The appropriate help message for flashing the given built artifact to the Squishy device.
		'''

		artifact_file = build_dir / name

		serial = ''
		if dev is not None:
			serial = f' -S {dev.serial}'

		msg = f'Use \'dfu-util\' to flash \'{artifact_file}\' into slot {slot}\n'
		msg += f'e.g. \'dfu-util -d {USB_VID:04X}:{USB_APP_PID:04X},:{USB_DFU_PID:04X}{serial} -a {slot} -R -D {artifact_file}\'\n'

		return msg

	def dump_utilization(self, name: str, products: LocalBuildProducts) -> None:
		'''
		Print out resource utilization and fmax timing info from the build.

		Parameters
		----------
		name : str
			The name of the built resource.

		products : LocalBuildProducts
			The build products
		'''

		pnr_rpt = json.loads(products.get(f'{name}.tim.json', 't'))

		log.debug('Clock network Fmax:')
		for net, fmax in pnr_rpt['fmax'].items():
			log.debug(f'    \'{net}\': {fmax["achieved"]:.2f}MHz (min: {fmax["constraint"]:.2f}MHz)')

		log.debug('Resource Utilization:')
		for name, util in pnr_rpt['utilization'].items():
			used: int      = util['used']
			available: int = util['available']
			log.debug(f'    {name:>15}: {used:>5}/{available:>5} ({(used/available) * 100.0:>6.2f}%)')
