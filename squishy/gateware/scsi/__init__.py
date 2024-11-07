# SPDX-License-Identifier: BSD-3-Clause

'''

Anatomy of a SCSI Bus
---------------------

SCSI Is a bus based system, all devices on the bus have a unique ID and are split into two categories,
Initiator, and Target. In general Initiators are show as an adapter connected to a host, and Targets are
shown as controllers attaches to a target device. This abstraction serves to represent that there can be
multiple possible targets behind a single controller, which share a single bus connection.

As SCSI is not a purely point-to-point bus, and allows for multiple bus initiators, there are three possible
bus topologies. The first is Single Initiator, Single Target. This topology acts as a point-to-point bus between
a SCSI Initiator and SCSI Target. The second being Single Initiator, Multiple Target. This topology is the
traditional topology along with Single Initiator that people think of when they think of SCSI. The final possible
common bus topology is Multiple Initiator, Multiple Target. This is where there are multiple initiators and multiple
targets all on the shared bus.

.. graphviz::
	:align: center
	:caption: Single Initiator, Single Target Bus Topology

	graph scsi_bus_sist {
		fontname="Fira Code"
		bgcolor="#FFFFFF00"
		node [fontname="Fira Code"]
		edge [fontname="Fire Code"]
		rankdir=LR;

		node [shape = Mrecord];

		H0 [label = "{<f0>HOST|<f1>ADAPTER}"];
		T0 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];

		H0:f1 -- T0:f0
	}



.. graphviz::
	:align: center
	:caption: Single Initiator, Multiple Target Bus Topology

	graph scsi_bus_simt {
		fontname="Fira Code"
		bgcolor="#FFFFFF00"
		node [fontname="Fira Code"]
		edge [fontname="Fire Code"]
		rankdir=LR;

		node [shape = Mrecord];

		H0 [label = "{<f0>HOST|<f1>ADAPTER}"];
		T0 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];
		T1 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];

		H0:f1 -- T0:f0
		H0:f1 -- T1:f0
	}

.. graphviz::
	:align: center
	:caption: Multiple Initiator, Multiple Target Bus Topology

	graph scsi_bus_mimt {
		fontname="Fira Code"
		bgcolor="#FFFFFF00"
		node [fontname="Fira Code"]
		edge [fontname="Fire Code"]
		rankdir=LR;

		node [shape = Mrecord];

		H0 [label = "{<f0>HOST|<f1>ADAPTER}"];
		H1 [label = "{<f0>HOST|<f1>ADAPTER}"];
		H2 [label = "{<f0>HOST|<f1>ADAPTER}"];

		T0 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];
		T1 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];
		T2 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];
		T3 [label = "{<f0>CONTROLLER|{<f1>TARGET|{LUN0|...}}}"];

		H0:f1 -- T0:f0
		H0:f1 -- T1:f0
		H0:f1 -- T2:f0
		H0:f1 -- T3:f0

		H1:f1 -- T0:f0
		H1:f1 -- T1:f0
		H1:f1 -- T2:f0
		H1:f1 -- T3:f0

		H2:f1 -- T0:f0
		H2:f1 -- T1:f0
		H2:f1 -- T2:f0
		H2:f1 -- T3:f0
	}

.. todo:: this, nya

.. graphviz::
	:align: center
	:caption: Arbitrating SCSI Bus State Machine

	digraph scsi_with_arbitration{
		fontname="Fira Code"
		bgcolor="#FFFFFF00"
		node [fontname="Fira Code"]
		edge [fontname="Fire Code"]
		rankdir=LR;
		node [shape = none]; _
		node [shape = doublecircle]; BF
		node [shape = circle];


		_ [label = "RESET"];
		BF [label = "BUS FREE"];
		A [label = "ARBITRATION"];
		S [label = "SELECTION"];
		R [label = "RESELECTION"];
		C [label = "COMMAND"];
		D [label = "DATA"];
		ST [label = "STATUS"];
		M [label = "MESSAGE"];

		subgraph CDSM {
			C -> C
			C -> D
			C -> ST
			C -> M

			D -> D
			D -> C
			D -> ST
			D -> M

			ST -> ST
			ST -> C
			ST -> D
			ST -> M

			M -> M
			M -> C
			M -> D
			M -> ST
		}

		S -> C [label = ""];
		S -> D [label = ""];
		S -> ST [label = ""];
		S -> M [label = ""];

		R -> C [label = ""];
		R -> D [label = ""];
		R -> ST [label = ""];
		R -> M [label = ""];

		_ -> BF [label = ""];
		BF -> A [label = ""];
		A -> S [label = ""];
		A -> R [label = ""];
		A -> BF [label = ""];
		S -> BF [label = ""];
		R -> BF [label = ""];

		C -> BF [label = ""];
		D -> BF [label = ""];
		ST -> BF [label = ""];
		M -> BF [label = ""];
	}

.. graphviz::
	:align: center
	:caption: Non-Arbitrating SCSI Bus State Machine

	digraph scsi_without_arbitration {
		fontname="Fira Code"
		bgcolor="#FFFFFF00"
		node [fontname="Fira Code"]
		edge [fontname="Fire Code"]
		rankdir=LR;
		node [shape = none]; _
		node [shape = doublecircle]; BF
		node [shape = circle];


		_ [label = "RESET"];
		BF [label = "BUS FREE"];
		S [label = "SELECTION"];
		C [label = "COMMAND"];
		D [label = "DATA"];
		ST [label = "STATUS"];
		M [label = "MESSAGE"];

		subgraph CDSM {
			C -> C
			C -> D
			C -> ST
			C -> M

			D -> D
			D -> C
			D -> ST
			D -> M

			ST -> ST
			ST -> C
			ST -> D
			ST -> M

			M -> M
			M -> C
			M -> D
			M -> ST
		}

		S -> C [label = ""];
		S -> D [label = ""];
		S -> ST [label = ""];
		S -> M [label = ""];

		_ -> BF [label = ""];
		BF -> S [label = ""];
		S -> BF [label = ""];

		C -> BF [label = ""];
		D -> BF [label = ""];
		ST -> BF [label = ""];
		M -> BF [label = ""];
	}


The following table lists the timing requirements for each SCSI version.

+-----------------------+--------------+--------------+--------------+
|  Name                 | SCSI1        | SCSI2        | SCSI3        |
+=======================+==============+==============+==============+
| Arbitration           | 2.2us        | 2.4us        | 2.4us        |
+-----------------------+--------------+--------------+--------------+
| Assertion             | 90ns         | 90ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Bus Clear             | 800ns        | 800ns        | 800ns        |
+-----------------------+--------------+--------------+--------------+
| Bus Free              | 800ns        | 800ns        | 800ns        |
+-----------------------+--------------+--------------+--------------+
| Bus Set               | 1.8us        | 1.8us        | 1.6us        |
+-----------------------+--------------+--------------+--------------+
| Bus Settle            | 400ns        | 400ns        | 400ns        |
+-----------------------+--------------+--------------+--------------+
| Cable Skew            | 10ns         | 10ns         | 4ns          |
+-----------------------+--------------+--------------+--------------+
| Data Release          | 400ns        | 400ns        | 400ns        |
+-----------------------+--------------+--------------+--------------+
| Deskew                | 45ns         | 45ns         | 45ns         |
+-----------------------+--------------+--------------+--------------+
| Hold Time             | 45ns         | 45ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Negation              | 90ns         | 90ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Reset Hold            | 25us         | 25us         | 25us         |
+-----------------------+--------------+--------------+--------------+
| Selection Abort       | 200us        | 200us        | 200us        |
+-----------------------+--------------+--------------+--------------+
| Selection Timeout     | 250ms        | 250ms        | 250ms        |
+-----------------------+--------------+--------------+--------------+
| Disconnect            | Unspecified  | 200us        | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Power to Selection    | Unspecified  | 10s          | 10s          |
+-----------------------+--------------+--------------+--------------+
| Reset to Selection    | Unspecified  | 250ms        | 250ms        |
+-----------------------+--------------+--------------+--------------+
| Fast Assert           | Unspecified  | 30ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Fast Cable Skew       | Unspecified  | 5ns          | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Fast Deskew           | Unspecified  | 20ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Fast Hold             | Unspecified  | 10ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+
| Fast Negation         | Unspecified  | 30ns         | Unspecified  |
+-----------------------+--------------+--------------+--------------+


''' # noqa: E101

__all__ = (

)
