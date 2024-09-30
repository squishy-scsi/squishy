# SPDX-License-Identifier: BSD-3-Clause
import logging                    as log

from abc                          import ABCMeta, abstractmethod
from argparse                     import ArgumentParser, Namespace
from pathlib                      import Path

from rich.progress                import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn
)

from ..core.device                import SquishyHardwareDevice
from ..gateware.platform.platform import SquishyPlatform
from ..gateware.platform          import AVAILABLE_PLATFORMS
from ..config                     import SQUISHY_BUILD_DIR


__all__ = (
	'SquishyAction',
	'SquishySynthAction',
)

class SquishyAction(metaclass = ABCMeta):
	'''
	Squishy action base class

	This is the abstract base class that is used
	to implement any possible action for the squishy
	command line interface.

	Attributes
	----------
	pretty_name : str
		The pretty name of the action to show.

	short_help : str
		A short help string for the action.

	help : str
		A more comprehensive help string for the action.

	description : str
		The description of the action.

	requires_dev : bool
		If this action requires a Squishy to be attached to the machine.

	'''
	@property
	@abstractmethod
	def pretty_name(self) -> str:
		''' The pretty name of the action  '''
		raise NotImplementedError('Actions must implement this property')

	@property
	@abstractmethod
	def short_help(self) -> str:
		''' A short help description for the action '''
		raise NotImplementedError('Actions must implement this property')

	@property
	def help(self) -> str:
		''' A longer help message for the action '''
		return '<HELP MISSING>'

	@property
	def description(self) -> str:
		''' A description for the action  '''
		return '<DESCRIPTION MISSING>'

	@property
	@abstractmethod
	def requires_dev(self) -> bool:
		''' Does this action require a squishy device to be attached '''
		raise NotImplementedError('Actions must implement this property')

	def __init__(self):
		pass

	@abstractmethod
	def register_args(self, parser: ArgumentParser) -> None:
		'''
		Register action arguments.

		When an action instance is initialized this method is
		called so when :py:func:`run` is called any needed
		arguments can be passed to the action.

		Parameters
		----------
		parser : argparse.ArgumentParser
			The argument parser to register commands with.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.

		'''

		raise NotImplementedError('Actions must implement this method')

	@abstractmethod
	def run(self, args: Namespace, dev: SquishyHardwareDevice | None = None) -> int:
		'''
		Run the action.

		Run the action instance, passing the parsed
		arguments and the selected device if any.

		Parameters
		----------
		args : argsparse.Namespace
			Any command line arguments passed.

		dev : Optional[squishy.core.device.SquishyHardwareDevice]
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
	This class is a sub-type of :py:class:`SquishyAction` that is dedicated to actions
	that deal with building gateware for Squishy hardware platforms.

	It centralizes the needed arguments for gateware Synthesis as well as Place and Routing,
	allowing for it to be updated without needing duplicated effort.

	'''

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)


	def get_hw_platform(
		self, args: Namespace, dev: SquishyHardwareDevice | None
	) -> tuple[SquishyPlatform, str, SquishyHardwareDevice] | None:
		''' Acquire the connected or specified hardware platform '''
		if not args.build_only and dev is None:
			dev = SquishyHardwareDevice.get_device(serial = args.device)

			if dev is None:
				log.error('No device selected, unable to continue.')
				return None

			hardware_platform = f'rev{dev.rev}'
			if hardware_platform not in AVAILABLE_PLATFORMS.keys():
				log.error(f'Unknown hardware revision \'{hardware_platform}\'')
				log.error(f'Expected one of {", ".join(AVAILABLE_PLATFORMS.keys())}')
				return None
		else:
			hardware_platform = args.hardware_platform

		log.info(f'Targeting platform \'{hardware_platform}\'')
		return (AVAILABLE_PLATFORMS[hardware_platform](), hardware_platform, dev)


	def run_synth(
		self, args: Namespace, plat: SquishyPlatform, elab, elab_name: str, cacheable: bool = False
	): # -> tuple[str, LocalBuildProducts]:
		''' Run Synthesis and Place and Route '''

		synth_opts: list[str] = []
		pnr_opts: list[str] = []
		pack_ops: list[str] = []
		script_pre_synth = ''
		script_post_synth = ''

		build_dir = Path(args.build_dir)

		if not build_dir.exists():
			log.debug(f'Making build directory {args.build_dir}')
			build_dir.mkdir()
		else:
			log.debug(f'Using build directory {args.build_dir}')

		# Build Options
		if cacheable:
			skip_cache = args.skip_cache
		else:
			skip_cache = True

		# Synthesis Options
		if not args.no_abc9:
			synth_opts.append('-abc9')
		if args.aggressive_mapping:
			if args.no_abc9:
				log.error('Can not spcify `--aggressive-mapping` with ABC9 disabled, remove `--no-abc9`')
			else:
				script_pre_synth += 'scratchpad -copy abc9.script.flow3 abc9.script\n'

		# Place and Route Options
		if args.use_router2:
			pnr_opts.append('--router router2')
		else:
			pnr_opts.append('--router router1')

		if args.tmg_ripup:
			pnr_opts.append('--tmg-ripup')

		if args.detailed_timing_report:
			pnr_opts.append('--report timing.json')
			pnr_opts.append('--detailed-timing-report')

		if args.routed_svg is not None:
			svg_path = args.routed_svg.resolve()
			log.info(f'Writing PnR output svg to {svg_path}')
			pnr_opts.append(f'--routed-svg {svg_path}')

		if args.routed_json is not None:
			json_path = args.routed_json.resolve()
			log.info(f'Writing PnR output json to {json_path}')
			pnr_opts.append(f'--write {json_path}')

		if args.pnr_seed is not None:
			pnr_opts.append(f'--seed {args.pnr_seed}')

		# Bitstream packing options

		if args.compress:
			pack_ops.append('--compress')

		# Actually do the build
		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:
			name, prod = plat.build(
				elab,
				name               = elab_name,
				build_dir          = build_dir,
				do_build           = True,
				do_program         = False,
				synth_opts         = synth_opts,
				nextpnr_opts       = pnr_opts,
				ecppack_opts       = pack_ops,
				verbose            = args.loud,
				skip_cache         = skip_cache,
				progress           = progress,
				debug_verilog      = cacheable and not skip_cache,
				script_after_read  = script_pre_synth,
				script_after_synth = script_post_synth
			)

			return (name, prod)

	def register_synth_args(self, parser: ArgumentParser, cacheable: bool = False) -> None:
		''' Register the common gateware options '''

		parser.add_argument(
			'--platform', '-p',
			dest    = 'hardware_platform',
			type    = str,
			default = list(AVAILABLE_PLATFORMS.keys())[-1],
			choices = list(AVAILABLE_PLATFORMS.keys()),
			help    = 'The target hardware platform if using --build-only',
		)

		gateware_options = parser.add_argument_group('Gateware Options')

		synth_options = parser.add_argument_group('Synthesis Options')
		pnr_options   = parser.add_argument_group('Place and Route Options')
		pack_options  = parser.add_argument_group('Packing Options')

		gateware_options.add_argument(
			'--build-only',
			action = 'store_true',
			help   = 'Only build the gateware, skip device programming'
		)

		if cacheable:
			gateware_options.add_argument(
				'--skip-cache',
				action = 'store_true',
				help   = 'Skip gateware cache lookup and subsequent caching of resultant gateware'
			)

		gateware_options.add_argument(
			'--build-dir', '-b',
			type = str,
			default = SQUISHY_BUILD_DIR,
			help    = 'The output directory for Squishy binaries and firmware images'
		)

		gateware_options.add_argument(
			'--loud',
			action = 'store_true',
			help   = 'Enables verbose output of Synthesis and PnR runs'
		)

		# Synthesis Options
		synth_options.add_argument(
			'--no-abc9',
			action = 'store_true',
			help   = 'Disable use of Yosys\' ABC9'
		)

		synth_options.add_argument(
			'--aggressive-mapping',
			action = 'store_true',
			help   = 'Run multiple ABC9 mapping more than once to improve performance in exchange for longer synth time'
		)

		# Place and Route Options
		pnr_options.add_argument(
			'--use-router2',
			action = 'store_true',
			help   = 'Use nextpnr\'s \'router2\' routing engine rather than \'router1\''
		)

		pnr_options.add_argument(
			'--tmg-ripup',
			action  = 'store_true',
			help    = 'Use the timing-driven ripup router'
		)

		pnr_options.add_argument(
			'--detailed-timing-report',
			action = 'store_true',
			help   = 'Have nextpnr output a detailed net timing report'
		)

		pnr_options.add_argument(
			'--routed-svg',
			type    = Path,
			default = None,
			help    = 'Write a render of the routing to an SVG'
		)

		pnr_options.add_argument(
			'--routed-json',
			type    = Path,
			default = None,
			help   = 'Write the PnR output json for viewing in nextpnr after PnR'
		)

		pnr_options.add_argument(
			'--pnr-seed',
			type    = int,
			default = 0,
			help    = 'Specify the PnR seed to use'
		)

		pnr_options.add_argument(
			'--hunt-n-peck',
			action = 'store_true',
			help   = 'If PnR fails with given seed, try to find one that passes timing'
		)

		# Bitstream packing options

		pack_options.add_argument(
			'--compress',
			action = 'store_true',
			help   = 'Compress resulting bitstream (Only for ECP5 based Squishy Platforms)'
		)
