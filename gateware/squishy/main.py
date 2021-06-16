# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

from .usb import USBDevice
from .scsi import SCSIInterface

class SquishyTop(Elaboratable):
	def elaborate(self, platform):
		m = Module()

		clk = platform.request('clk')
		m.domains.sync = ClockDomain()
		m.d.comb += ClockSignal().eq(clk.i)

		m.submodules.scsi = scsi = SCSIInterface()
		m.submodules.usb = usb = USBDevice()

		leds = platform.request('leds')

		m.d.comb += [

		]

		return m
