# SPDX-License-Identifier: BSD-3-Clause
from typing         import (
	Literal, Union, Optional
)

from torii.build import (
	Attrs, Pins, PinsN, Subsignal, DiffPairs, Resource
)

__all__ = (
	'SCSIConnectorResource',
	'SCSIDifferentialResource',
	'SCSISingleEndedResource',
	'SCSIPhyResource',
)

__doc__ = '''\

'''

# Type Aliases
PinDiff = tuple[str, str]
PinDef  = Union[str, PinDiff]
PinDir  = Literal['i', 'o', 'io']

def TransceiverPairs(
	tx: str, rx: str, *,
	invert: bool = False, conn: str = None,
	assert_width: Optional[int] = None
) -> tuple[Subsignal]:
	'''
	Returns a tuple of subsignals for RX and TX pairs

	Parameters
	----------
	tx : str
		The PHY TX pins.

	rx : str
		The PHY RX pins.

	invert : bool
		If the signals are inverted or not,

	conn : str
		The connector, if any.

	assert_width : int
		The width of the pin pairs.

	Returns
	-------
	tuple[Subsignal, Subsignal]
		The RX/TX pair with correct directions and inversion set up.

	'''
	return (
		Subsignal('tx', Pins(tx, dir = 'o', invert = invert, conn = conn, assert_width = assert_width)),
		Subsignal('rx', Pins(rx, dir = 'i', invert = invert, conn = conn, assert_width = assert_width)),
	)

def SCSIConnectorResource(*args, diff: bool,
	ack: PinDef, atn: PinDef, bsy: PinDef, cd: PinDef, io: PinDef, msg: PinDef,
	sel: PinDef, req: PinDef, rst: PinDef, diff_sense: str, d0: PinDef, dp0: PinDef,
	d1: Optional[PinDef] = None, dp1: Optional[PinDef]  = None, scsi_id: Optional[str] = None,
	led: Optional[str]  = None, spindle: Optional[str] = None, rmt: Optional[str] = None,
	dlyd: Optional[str] = None, dir: PinDir = 'io', attrs: Optional[Attrs]   = None) -> Resource:
	'''
	Represents a raw SCSI connector

	Parameters
	----------
	diff : bool
		If the SCSI connector is Differential.

	ack : str, tuple[str, str]
		The pin or pins for the SCSI ACK signal.

	atn : str, tuple[str, str]
		The pin or pins for the SCSI ATN signal.

	bsy : str, tuple[str, str]
		The pin or pins for the SCSI BSY signal.

	cd : str, tuple[str, str]
		The pin or pins for the SCSI CD signal.

	io : str, tuple[str, str]
		The pin or pins for the SCSI IO signal.

	msg : str, tuple[str, str]
		The pin or pins for the SCSI MSG signal.

	req : str, tuple[str, str]
		The pin or pins for the SCSI REQ signal.

	rst : str, tuple[str, str]
		The pin or pins for the SCSI RST signal.

	diff_sense : str
		The SCSI differential sense pin.

	d0 : str, tuple[str, str]
		The pin set or set of pin sets for the first SCSI data byte lines.

	dp0 : str, tuple[str, str]
		The pin or pins for the first SCSI data byte parity bit.

	Other Parameters
	----------------
	d1 : str, tuple[str, str]
		The pin set or set of pin sets for the second SCSI data byte lines.

	dp1 : str, tuple[str, str]
		The pin or pins for the second SCSI data byte parity bit.

	scsi_id : str
		The pin set of set of pin sets for the dedicated SCSI_ID pins.

	led : str
		The SCSI bus LED signal pin.

	spindle : str
		The SCSI spindle signal pin.

	rmt : str
		The SCSI RMT signal pin.

	dlyd : str
		The SCSI dlyd signal pin.

	dir : str
		The direction of the SCSI connector pins, defaults to 'io'

	Returns
	-------
	:py:class:`torii.build.dsl.Resource`
		The SCSI Connector Resource

	'''

	if diff:
		io = [
			Subsignal('ack',        DiffPairs(*ack,  dir = dir, assert_width = 1)),
			Subsignal('atn',        DiffPairs(*atn,  dir = dir, assert_width = 1)),
			Subsignal('bsy',        DiffPairs(*bsy,  dir = dir, assert_width = 1)),
			Subsignal('cd',         DiffPairs(*cd,   dir = dir, assert_width = 1)),
			Subsignal('io',         DiffPairs(*io,   dir = dir, assert_width = 1)),
			Subsignal('msg',        DiffPairs(*msg,  dir = dir, assert_width = 1)),
			Subsignal('sel',        DiffPairs(*sel,  dir = dir, assert_width = 1)),
			Subsignal('req',        DiffPairs(*req,  dir = dir, assert_width = 1)),
			Subsignal('rst',        DiffPairs(*rst,  dir = dir, assert_width = 1)),
			Subsignal('d0',         DiffPairs(*d0,   dir = dir, assert_width = 8)),
			Subsignal('dp0',        DiffPairs(*dp0,  dir = dir, assert_width = 1)),
			Subsignal('diff_sense', Pins(diff_sense, dir = dir, assert_width = 1)),
		]
	else:
		io = [
			Subsignal('ack',        Pins(ack,        dir = dir, assert_width = 1)),
			Subsignal('atn',        Pins(atn,        dir = dir, assert_width = 1)),
			Subsignal('bsy',        Pins(bsy,        dir = dir, assert_width = 1)),
			Subsignal('cd',         Pins(cd,         dir = dir, assert_width = 1)),
			Subsignal('io',         Pins(io,         dir = dir, assert_width = 1)),
			Subsignal('msg',        Pins(msg,        dir = dir, assert_width = 1)),
			Subsignal('sel',        Pins(sel,        dir = dir, assert_width = 1)),
			Subsignal('req',        Pins(req,        dir = dir, assert_width = 1)),
			Subsignal('rst',        Pins(rst,        dir = dir, assert_width = 1)),
			Subsignal('d0',         Pins(d0,         dir = dir, assert_width = 8)),
			Subsignal('dp0',        Pins(dp0,        dir = dir, assert_width = 1)),
			Subsignal('diff_sense', Pins(diff_sense, dir = dir, assert_width = 1)),
		]

	if d1 is not None:
		assert dp1 is not None, 'Parity bit for d1 must be present'
		if diff:
			io.append(Subsignal('d1',  DiffPairs(*d1,  dir = dir, assert_width = 8))),
			io.append(Subsignal('dp1', DiffPairs(*dp1, dir = dir, assert_width = 1))),
		else:
			io.append(Subsignal('d1',  Pins(d1,  dir = dir, assert_width = 8))),
			io.append(Subsignal('dp1', Pins(dp1, dir = dir, assert_width = 1))),

	if scsi_id is not None:
		assert led is not None
		assert spindle is not None
		assert rmt is not None
		assert dlyd is not None

		io.append(Subsignal('id',      Pins(scsi_id, dir = dir, assert_width = 4))),
		io.append(Subsignal('led',     Pins(led,     dir = dir, assert_width = 1))),
		io.append(Subsignal('spindle', Pins(spindle, dir = dir, assert_width = 1))),
		io.append(Subsignal('rmt',     Pins(rmt,     dir = dir, assert_width = 1))),
		io.append(Subsignal('dlyd',    Pins(dlyd,    dir = dir, assert_width = 1))),

	if attrs is not None:
		io.append(attrs)

	return Resource.family(*args, default_name = 'scsi_conn', ios = io)


def SCSIPhyResource(*args,
	ack: PinDiff, atn: PinDiff, bsy: PinDiff, cd: PinDiff, io: PinDiff, msg: PinDiff,
	sel: PinDiff, req: PinDiff, rst: PinDiff, d0: PinDiff, dp0: PinDiff,
	tp_en: str, tx_en: str, aa_en: str, bsy_en: str, sel_en: str, mr_en: str,
	diff_sense: str, d1: Optional[PinDiff] = None, dp1: Optional[PinDiff] = None,
	scsi_id: Optional[PinDiff] = None, led: Optional[PinDiff] = None,
	spindle: Optional[PinDiff] = None, rmt: Optional[PinDiff] = None,
	dlyd: Optional[PinDiff] = None, attrs: Optional[Attrs] = None) -> Resource:
	'''
	Represents a Squishy SCSI PHY Resource

	Parameters
	----------
	ack : tuple[str, str]
		The pins for the SCSI ACK tx and rx signals.

	atn : tuple[str, str]
		The pins for the SCSI ATN tx and rx signals.

	bsy : tuple[str, str]
		The pins for the SCSI BSY tx and rx signals.

	cd : tuple[str, str]
		The pins for the SCSI CD tx and rx signals.

	io : tuple[str, str]
		The pins for the SCSI IO tx and rx signals.

	msg : tuple[str, str]
		The pins for the SCSI MSG tx and rx signals.

	sel : tuple[str, str]
		The pins for the SCSI SEL tx and rx signals.

	req : tuple[str, str]
		The pins for the SCSI REQ tx and rx signals.

	rst : tuple[str, str]
		The pins for the SCSI RST tx and rx signals.

	d0 : tuple[str, str]
		The pins for the SCSI data byte one tx and rx signals.

	dp0 : tuple[str, str]
		The pins for the SCSI data byte one parity tx and rx signals.

	tp_en : str
		The enable pin for the TP portion of the PHY.

	tx_en : str
		The enable pin for the TX portion of the PHY.

	aa_en : str
		The enable pin for the AA portion of the PHY.

	bsy_en : str
		The enable pin for the BSY portion of the PHY.

	sel_en : str
		The enable pin for the SEL portion of the PHY.

	mr_en : str
		The enable pin for the MSG/REQ portion of the PHY.

	diff_sense : str
		The SCSI bus DIFF_SENSE pin.

	Returns
	-------
	:py:class:`torii.build.dsl.Resource`
		The SCSI Connector Resource

	'''

	io = [
		Subsignal('ack',        *TransceiverPairs(*ack,                  assert_width = 1)),
		Subsignal('atn',        *TransceiverPairs(*atn,                  assert_width = 1)),
		Subsignal('bsy',        *TransceiverPairs(*bsy,                  assert_width = 1)),
		Subsignal('cd',         *TransceiverPairs(*cd,                   assert_width = 1)),
		Subsignal('io',         *TransceiverPairs(*io,                   assert_width = 1)),
		Subsignal('msg',        *TransceiverPairs(*msg,                  assert_width = 1)),
		Subsignal('sel',        *TransceiverPairs(*sel,                  assert_width = 1)),
		Subsignal('req',        *TransceiverPairs(*req,                  assert_width = 1)),
		Subsignal('rst',        *TransceiverPairs(*rst,                  assert_width = 1)),
		Subsignal('d0',         *TransceiverPairs(*d0,                   assert_width = 8)),
		Subsignal('dp0',        *TransceiverPairs(*dp0,                  assert_width = 1)),
		Subsignal('tp_en',                PinsN(tp_en,      dir = 'o',  assert_width = 1)),
		Subsignal('tx_en',                PinsN(tx_en,      dir = 'o',  assert_width = 1)),
		Subsignal('aa_en',                PinsN(aa_en,      dir = 'o',  assert_width = 1)),
		Subsignal('bsy_en',               PinsN(bsy_en,     dir = 'o',  assert_width = 1)),
		Subsignal('sel_en',               PinsN(sel_en,     dir = 'o',  assert_width = 1)),
		Subsignal('mr_en',                PinsN(mr_en,      dir = 'o',  assert_width = 1)),
		Subsignal('diff_sense',            Pins(diff_sense, dir = 'i',  assert_width = 1)),
	]

	if d1 is not None:
		assert dp1 is not None, 'Parity bit for d1 must be present'
		io.append(Subsignal('d1',  *TransceiverPairs(*d1,  assert_width = 8))),
		io.append(Subsignal('dp1', *TransceiverPairs(*dp1, assert_width = 1))),

	if scsi_id is not None:
		assert led is not None
		assert spindle is not None
		assert rmt is not None
		assert dlyd is not None

		io.append(Subsignal('id',      *TransceiverPairs(*scsi_id, assert_width = 4))),
		io.append(Subsignal('led',     *TransceiverPairs(*led,     assert_width = 1))),
		io.append(Subsignal('spindle', *TransceiverPairs(*spindle, assert_width = 1))),
		io.append(Subsignal('rmt',     *TransceiverPairs(*rmt,     assert_width = 1))),
		io.append(Subsignal('dlyd',    *TransceiverPairs(*dlyd,    assert_width = 1))),

	if attrs is not None:
		io.append(attrs)

	return Resource.family(*args, default_name = 'scsi_phy', ios = io)


def SCSIDifferentialResource(*args, **kwargs) -> SCSIConnectorResource:
	''' Constructs an explicitly differential :py:func:`SCSIConnectorResource` '''
	return SCSIConnectorResource(*args, diff = True, **kwargs)

def SCSISingleEndedResource(*args, **kwargs) -> SCSIConnectorResource:
	''' Constructs an explicitly single-ended :py:func:`SCSIConnectorResource` '''
	return SCSIConnectorResource(*args, diff = False, **kwargs)
