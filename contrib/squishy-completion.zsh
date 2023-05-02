#compdef squishy "python -m squishy"
# ln -sv squishy-completion.zsh _squishy
# unfunction _squishy && autoload -U _squishy
# SPDX-License-Identifier: BSD-3-Clause

_squishy_command() {
	local -a commands=(
		'applet[Squishy applet subsystem]'
		'cache[Squishy applet cache managment]'
		'provision[Squishy hardware provisioning]'
	)
	_values 'squishy commands' : $commands
}

_squishy_applet_command() {
	local -a commands=(
		'analyzer[Squishy SCSI analyzer]'
		'taperipper[UEFI Boot from 9-track tape]'
	)
	_values 'squishy applets' : $commands
}

_squishy_applet_analyzer() {
	local arguments

	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'

	)

	_arguments -s : $arguments
}

_squishy_applet_taperipper() {
	local arguments

	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'

	)

	_arguments -s : $arguments
}

_squishy_applet() {
	local arguments
	local platforms=`python -m squishy applet -h | tail -n +4 | grep -m1 -e '\-\-platform\s{' | sed 's/,\s-p\s.*$//' | sed 's/--platform\s{\([^}]*\)}/\1/'`

	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'
		'(-p --platforms)'{-p=,--platforms=}"[Target hardware platform]:platform:(${(s/,/)platforms})"

		'--skip-cache[Skip bitstream cache lookup]'
		'(-b --build-dir)'{-b,--build-dir}"[Output directory for build products]:dir:_directories"
		'--loud[Enables output from PnR and synthesis]'
		'--build-only[Only build the applet]'

		'--use-router2[Use nextpnrs router2 rather than router1]'
		'--tmp-ripup[Use timing driven ripup]'
		'--detailed-timing-report[Output a detailed timing report]'
		'--routed-svg[Save an svg of the routed output]:svg:_files -g "*.svg"'
		'--routed-json[Save routed json netlist]:json:_files -g "*.json"'
		'--pnr-seed[Specify PNR seed]:seed:_numbers -l 0 "PNR_SEED"'


		'--no-abc9[Disable ABC9 durring synthesis]'

		'--enable-webusb[Enable the experimental WebUSB support]'
		'--webusb-url=[WebUSB URL to encode]:url:_urls'

		'(-U --enable-uart)'{-U,--enable-uart}'[Enable debug UART]'
		'(-B --baud)'{-B,--baud}'=[Baud rate to run the debug UART at]:baud:_numbers -d 9600'
		'(-D --data-bits)'{-D,--data-bits}'=[Data bits to use for the debug UART]:data:_numbers -d 8'
		'(-c --parity)'{-c,--parity}'=[Parity mode to use for the debug UART]:parity:(none mark spaceeven odd)'

		'--scsi-did=[The SCSI ID to use]:scsi_id:_numbers -l 0 -m 7 "SCSI ID"'
		'--scsi-arbitrating[Enable SCSI bus arbitration]'

		'(-): :->applet'
		'(-)*:: :->applet_args'
	)

	_arguments -s : $arguments && return

	case $state in
		(applet)
			_squishy_applet_command && ret=0
			;;
		(applet_args)
			curcontext=${curcontext%:*:*}:squishy-$words[1]:
			case $words[1] in
				(analyzer)
					_squishy_applet_analyzer && ret=0
					;;
				(taperipper)
					_squishy_applet_taperipper && ret=0
					;;
			esac
			;;
	esac
	return $ret
}

_squishy_provision() {
	local arguments
	local platforms=`python -m squishy provision -h | tail -n +4 | grep -m1 -e '\-\-platform\s{' | sed 's/,\s-p\s.*$//' | sed 's/--platform\s{\([^}]*\)}/\1/'`

	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'
		'(-p --platforms)'{-p=,--platforms=}"[Target hardware platform]:platform:(${(s/,/)platforms})"

		'--skip-cache[Skip bitstream cache lookup]'
		'(-b --build-dir)'{-b,--build-dir}"[Output directory for build products]:dir:_directories"
		'--loud[Enables output from PnR and synthesis]'
		'--build-only[Only build the applet]'

		'--use-router2[Use nextpnrs router2 rather than router1]'
		'--tmp-ripup[Use timing driven ripup]'
		'--detailed-timing-report[Output a detailed timing report]'
		'--routed-svg[Save an svg of the routed output]:svg:_files -g "*.svg"'
		'--routed-json[Save routed json netlist]:json:_files -g "*.json"'
		'--pnr-seed[Specify PNR seed]:seed:_numbers -l 0 "PNR_SEED"'

		'--no-abc9[Disable ABC9 durring synthesis]'

		'(-S --serial-number)'{-S,--serial-number}'[Specify Serial Number to use]'
		'(-W --whole-device)'{-W,--whole-device}'=[Generate a whole device provisioning image for factory progrssming]'
	)

	_arguments -s : $arguments && return


	return 0
}

_squishy_cache_command() {
	local -a commands=(
		'list[Show cache status]'
		'clear[Clear cache]'
	)
	_values 'squishy cache' : $commands
}

_squishy_cache_list() {
	local arguments
	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'
		'--list-cache-items[List each item in the cache (WARNING: CAN BE LARGE)]'
	)

	_arguments -s : $arguments
}

_squishy_cache_clear() {
	local arguments
	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'

	)

	_arguments -s : $arguments
}

_squishy_cache() {
	local arguments
	integer ret=1

	arguments=(
		'(-h --help)'{-h,--help}'[Show help and exit]'

		'(-): :->action'
		'(-)*:: :->action_args'
	)

	_arguments -s : $arguments && return

	case $state in
		(action)
			_squishy_cache_command && ret=0
			;;
		(action_args)
			curcontext=${curcontext%:*:*}:squishy-$words[1]:
			case $words[1] in
				(list)
					_squishy_cache_list && ret=0
					;;
				(clear)
					_squishy_cache_clear && ret=0
					;;
			esac
			;;
	esac
	return $ret
}

_squishy() {
	local arguments context curcontext=$curcontext state state_descr line
	integer ret=1

	arguments=(
		'(-h --help)'{-h,--help}'[show version and help then exit]'
		'(-d --device)'{-d,--device}'=[specify device serial number]'
		'(-v --verbose)'{-v,--verbose}'[verbose logging]'
		'(-): :->command'
		'(-)*:: :->arguments'
	)

	_arguments -s -C : $arguments && return

	case $state in
		(command)
			_squishy_command && ret=0
			;;
		(arguments)
			curcontext=${curcontext%:*:*}:squishy-$words[1]:
			case $words[1] in
				(applet)
					_squishy_applet && ret=0
					;;
				(cache)
					_squishy_cache && ret=0
					;;
				(provision)
					_squishy_provision && ret=0
			esac
			;;
	esac

	return $ret
}

_squishy
