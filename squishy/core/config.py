# SPDX-License-Identifier: BSD-3-Clause

'''
This module contains various classes and types
for making dealing with things like configuration
and command line argument options more sane.

This file also contains the various "set in stone" constants
that are used for default/constant initialization.
'''

from typing import TypeAlias

from .flash import Geometry as FlashGeometry

__all__ = (
	# PLL Configurations for the various hardware platforms
	'ICE40PLLConfig',
	'ECP5PLLOutput',
	'ECP5PLLConfig',
	'PLLConfig', # Type Alias
	# Peripherals
	'USBConfig',
	'SCSIConfig',
	'FlashConfig',

	# Fixed/Default configurations
	'USB_DFU_CONFIG',
)

# Constants

USB_VID          = 0x1209
USB_DFU_PID      = 0xCA71
USB_APP_PID      = 0xCA70

USB_MANUFACTURER = 'Shrine Maiden Heavy Industries'

SCSI_VID = 'Shrine-0'

# Configuration Wrappers

class ICE40PLLConfig:
	'''
	An iCE40 SB_PLL40_PAD PLL Configuration

	This is only used for the :py:class:`squishy.gateware.rev1` platform.

	Parameters
	----------
	divr : int
		PLL reference clock divisor.

	divf : int
		PLL feedback divisor.

	divq : int
		PLL VCO divisor.

	filter_range : int
		PLL filter range.

	ofreq : int
		The output frequency of the PLL in MHz


	Attributes
	----------
	divr : int
		PLL reference clock divisor.

	divf : int
		PLL feedback divisor.

	divq : int
		PLL VCO divisor.

	filter_range : int
		PLL filter range.

	ofreq : int
		The output frequency of the PLL in MHz

	'''

	def __init__(self, *, divr: int, divf: int, divq: int, filter_range: int, ofreq: int) -> None:
		self.divr         = divr
		self.divf         = divf
		self.divq         = divq
		self.filter_range = filter_range
		self.ofreq        = ofreq

class ECP5PLLOutput:
	'''
	A ECP5 EHXPLLL output, either the primary output or any of the 3 auxillary outputs.

	Parameters
	----------
	ofreq : int
		The frequency of this PLL output in MHz

	clk_div : int
		The clock divisor of this PLL output

	cphase : int
		The clock phase of this PLL output

	fphase : int
		The feedback phase of this PLL output

	Attributes
	----------
	ofreq : int
		The frequency of this PLL output in MHz

	clk_div : int
		The clock divisor of this PLL output

	cphase : int
		The clock phase of this PLL output

	fphase : int
		The feedback phase of this PLL output
	'''

	def __init__(self, *, ofreq: int, clk_div: int, cphase: int, fphase: int) -> None:
		self.ofreq   = ofreq
		self.clk_div = clk_div
		self.cphase  = cphase
		self.fphase  = fphase

class ECP5PLLConfig:
	'''
	A ECP5 EHXPLLL configuration

	Parameters
	----------
	ifreq : int
		The PLLs input clock frequency in MHz

	clki_div : int
		The PLL input clock divisor

	clkfb_div : int
		The PLL feedback clock divisor

	clkp : ECP5PLLOutput
		The Primary PLL output clock configuration

	clks : ECP5PLLOutput
		The secondary PLL output clock configuration

	clks2 : ECP5PLLOutput | None
		The optional tertiary PLL output clock configuration

	clks3 : ECP5PLLOutput | None
		The optional quaternary PLL output clock configuration

	Attributes
	----------
	ifreq : int
		The PLLs input clock frequency in MHz

	clki_div : int
		The PLL input clock divisor

	clkfb_div : int
		The PLL feedback clock divisor

	clkp : ECP5PLLOutput
		The Primary PLL output clock configuration

	clks : ECP5PLLOutput | None
		The optional secondary PLL output clock configuration

	clks2 : ECP5PLLOutput | None
		The optional tertiary PLL output clock configuration

	clks3 : ECP5PLLOutput | None
		The optional quaternary PLL output clock configuration

	'''

	def __init__(
			self, *,
			ifreq: int, clki_div: int, clkfb_div: int,
			clkp: ECP5PLLOutput,
			clks: ECP5PLLOutput  | None = None,
			clks2: ECP5PLLOutput | None = None,
			clks3: ECP5PLLOutput | None = None,
		) -> None:

		self.ifreq     = ifreq
		self.clki_div  = clki_div
		self.clkfb_div = clkfb_div
		self.clkp      = clkp
		self.clks      = clks
		self.clks2     = clks2
		self.clks3     = clks3

PLLConfig: TypeAlias = ECP5PLLConfig | ICE40PLLConfig

class USBConfig:
	'''
	USB Device Configuration Options

	Parameters
	----------
	vid : int
		The USB Vendor ID

	pid : int
		The USB Product ID

	mfr : str
		The manufacturer field of the USB descriptor

	prod : str
		The product field of the USB descriptor

	Attributes
	----------
	vid : int
		The USB Vendor ID

	pid : int
		The USB Product ID

	manufacturer : str
		The manufacturer field of the USB descriptor

	product : str
		The product field of the USB descriptor
	'''

	def __init__(self, *, vid: int, pid: int, mfr: str, prod: str) -> None:
		self.vid          = vid
		self.pid          = pid
		self.manufacturer = mfr
		self.product      = prod

# TODO(aki): We should probably support all of the `INQUIRY` fields here, maybe
class SCSIConfig:
	'''
	SCSI Configuration

	Parameters
	----------
	vid : str
		The SCSI Vendor ID.

	did : str
		The SCSI Target/Initiator ID.

	Attributes
	----------
	vid : str
		The SCSI Vendor ID.

	did : int
		The SCSI Target/Initiator ID.
	'''

	def __init__(self, *, vid: str, did: int) -> None:
		self.vid = vid
		self.did = did


class FlashConfig:
	'''
	Configuration options for attached SPI boot flash.

	Attributes
	----------
	geometry : FlashGeometry
		The layout of the on-board flash
	commands : dict[str, int] | None
		The optional mapping of command name to opcode
	'''

	def __init__(self, *, geometry: FlashGeometry, commands: dict[str, int] | None = None) -> None:
		self.geometry = geometry
		self.commands = commands


# Static/Default configurations

USB_DFU_CONFIG = USBConfig(
	vid  = USB_VID,
	pid  = USB_DFU_PID,
	mfr  = USB_MANUFACTURER,
	prod = 'Squishy DFU'
)

USB_APP_CONFIG = USBConfig(
	vid  = USB_VID,
	pid  = USB_APP_PID,
	mfr  = USB_MANUFACTURER,
	prod = 'Squishy'
)
