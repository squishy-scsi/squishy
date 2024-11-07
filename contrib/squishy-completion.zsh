#compdef squishy "python -m squishy"
# ln -sv squishy-completion.zsh _squishy
# unfunction _squishy && autoload -U _squishy
# SPDX-License-Identifier: BSD-3-Clause

_squishy_command() {
	local -a commands=(
		'applet[Squishy applet subsystem]'
		'provision[Squishy hardware provisioning]'
	)
	_values 'squishy commands' : $commands
}

_squishy_applet_command() {
	local -a commands=(
		'analyzer[Squishy SCSI analyzer]'
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

_squishy_applet() {
	local arguments
	local platforms=`python -m squishy applet -h | tail -n +4 | grep -m1 -e '--platform\s{' | sed 's/,\s-p\s.*$//' | sed 's/--platform\s{\([^}]*\)}/\1/'`

	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'
		'(-p --platforms)'{-p=,--platforms=}"[Target hardware platform]:platform:(${(s/,/)platforms})"

		'(-Y --noconfirm)'{-Y,--noconfirm}'[Do not ask for confirmation if the target applet is in preview]'
		'(-F --flash)'{-f,--flash}'[Flash the applet into persistent storage raather then doing an ephemeral load if supported]'

		'(-B --build-only)'{-B,--build-only}'[Only build and pack the applet, skip device programming]'
		'(-b --build-dir)'{-b,--build-dir}"[Output directory for build products]:dir:_directories"
		'(-C --skip-cache)'{-C,--skip-cache}'[Skip artifact cache lookup and squesequent insertion when build is completed]'
		'--build-verbose[Enable verbose tool output during build]'

		'--no-abc9[Disable use of abc9, will likely result in worse applet performance]'
		'--no-aggressive-mapping[Disable multiple abc9 passes, speeds up build time in exchange for worse performance]'

		'--detailed-report[Output a detailed timing report]'
		'--no-routed-netlist[Do not save routed json netlist]'
		'--pnr-seed[Specify PNR seed]:seed:_numbers -l 0 "PNR_SEED"'

		'--dont-compress[Disable bitstream compression if supported on the platform]'

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
			esac
			;;
	esac
	return $ret
}

_squishy_provision() {
	local arguments
	local platforms=`python -m squishy provision -h | tail -n +4 | grep -m1 -e '--platform\s{' | sed 's/,\s-p\s.*$//' | sed 's/--platform\s{\([^}]*\)}/\1/'`

	arguments=(
		'(-h --help)'{-h,--help}'[Show help message and exit]'
		'(-p --platforms)'{-p=,--platforms=}"[Target hardware platform]:platform:(${(s/,/)platforms})"

		'(-Y --noconfirm)'{-Y,--noconfirm}'[Do not ask for confirmation if the target applet is in preview]'
		'(-F --flash)'{-f,--flash}'[Flash the applet into persistent storage raather then doing an ephemeral load if supported]'

		'(-B --build-only)'{-B,--build-only}'[Only build and pack the applet, skip device programming]'
		'(-b --build-dir)'{-b,--build-dir}"[Output directory for build products]:dir:_directories"
		'--build-verbose[Enable verbose tool output during build]'

		'--no-abc9[Disable use of abc9, will likely result in worse applet performance]'
		'--no-aggressive-mapping[Disable multiple abc9 passes, speeds up build time in exchange for worse performance]'

		'--detailed-report[Output a detailed timing report]'
		'--no-routed-netlist[Do not save routed json netlist]'
		'--pnr-seed[Specify PNR seed]:seed:_numbers -l 0 "PNR_SEED"'

		'--dont-compress[Disable bitstream compression if supported on the platform]'

		'(-S --serial-number)'{-S,--serial-number}'[Specify serial number to use]'
		'(-W --whole-device)'{-W,--whole-device}'=[Generate a whole device provisioning image for factory programming]'
	)

	_arguments -s : $arguments && return


	return 0
}


_squishy() {
	local arguments context curcontext=$curcontext state state_descr line
	integer ret=1

	arguments=(
		'(-h --help)'{-h,--help}'[show version and help then exit]'
		'(-d --device)'{-d,--device}'=[specify device serial number]'
		'(-v --verbose)'{-v,--verbose}'[verbose logging]'
		'(-V --version)'{-V,--version}'[show version and exit]'
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
				(provision)
					_squishy_provision && ret=0
			esac
			;;
	esac

	return $ret
}

_squishy
