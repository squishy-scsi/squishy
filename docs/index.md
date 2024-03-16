```{toctree}
:hidden:

introduction
install
getting_started
hardware/index
applets/index
library/index
tutorials/index
cli
extra
mascot
faq

changelog

Source Code <https://github.com/squishy-scsi/squishy>
Hardware <https://github.com/squishy-scsi/hardware>

```
# Squishy: The SCSI Multitool

```{eval-rst}
.. figure:: ../contrib/img/sachi/electrichearts_20220323A_sachi_trans.png
	:align: right
	:figwidth: 350px
```

This is the documentation for [Squishy] and its supporting components, as well as a collection of guides and tutorials for the Squishy ecosystem.


## What Squishy Isn't

It's important to detail what Squishy isn't, as it differs a lot from other devices intended to interact with older SCSI systems.

Squishy is not *only* a disk emulator like the [BlueSCSI] or the [SCSI2SD]. It is also not *only* a SCSI to USB Mass storage adapter.

Squishy is not a *specialized* device targeting only a single aspect of the SCSI ecosystem, nor targeting only a single platform.

## What Squishy Is

Squishy is a platform, it allows you to accomplish almost any goal you wish to that involves a SCSI bus. It can do things as mundane as emulating a SCSI hard drive, but also you can use it to [sniff, analyze, and replay SCSI bus traffic], or even [boot a modern system from 9-track tape].

You can think of Squishy as being "Software Defined SCSI", much like how a Software Defined Radio works with a hardware transceiver and a software ecosystem, Squishy provides the same, but for SCSI.

It is comprised of a [gateware] and [python] library as well as a [hardware] platform that acts as a bridge between the software and SCSI bus. Squishy allows for powerful and flexible control over all things SCSI, and using its [powerful applet system] it gives that power to you.


For a more detailed introduction to Squishy and it's components, see the [Introduction] section of the documentation. Then, when you're ready visit the [Getting Started] section to get up an running.

Squishy is entirely open source, and under permissive licenses. The full source code, gateware, firmware, and hardware designs are available on [GitHub].

## Comparison

|                       | [Squishy]              | [BlueSCSI]      | [SCSI2SD] | [PiSCSI]           |
|-----------------------|------------------------|-----------------|-----------|--------------------|
| Has a cute mascot     | Yes                    | No              | No        | No                 |
| Device Emulation      | Yes                    | Yes             | Yes       | Yes                |
| Non-Storage Emulation | Yes                    | Yes<sup>1</sup> | No        | Yes<sup>2</sup>    |
| Initiator Emulation   | Yes                    | Yes             | No        | Yes<sup>2</sup>    |
| Passive Bus Tapping   | Yes                    | No?             | No        | Yes                |
| Fully Open Source     | Yes                    | Yes             | No        | No<sup>3</sup>     |
| SCSI-1 Support        | Yes                    | Yes             | No        | No                 |
| SCSI-2 Support        | Yes                    | Yes             | Yes       | Yes                |
| SCSI-3 Support        | Yes                    | No              | No        | No                 |
| HVD Support           | Yes                    | No              | No        | No                 |
| LVD Support           | Yes                    | No              | No        | No                 |
| SE Support            | Yes                    | Yes             | Yes       | Yes                |
| Fastest Bus Speed     | ULTRA320<sup>4,5</sup> | FAST10          | FAST10    | FAST10?            |
| Standalone            | No<sup>6</sup>         | Yes             | Yes       | Yes                |
| Cost                  | ?<sup>7</sup>          | ~50USD          | ~98USD    | ~50USD<sup>8</sup> |

<small>**1:** Only supports DaynaPORT emulation.</small>

<small>**2:** PiSCSI allows you to write Linux userspace software via an API.</small>

<small>**3:** The adapter board is Open Source, but the main compute element is not.</small>

<small>**4:** Depends on the SCSI PHY Module and interface adapter.</small>

<small>**5:** Only ULTRA320 SCSI speeds are guaranteed, however, depending on the silicon lottery ULTRA640 may be achievable.</small>

<small>**6:** Squishy requires USB power for operation, therefore it is considered to always be tethered.</small>

<small>**7:** Due to the hardware not being 100% complete an accurate cost is not available yet.</small>

<small>**8:** This includes only the PiSCSI interface itself, and not the needed RaspberryPi SOM as well.</small>


## Community

Squishy has a dedicated IRC channel, [#squishy on libera.chat]. Join to ask questions, discuss ongoing development, or just hang out.

There are also [GitHub Discussions] enabled on the repository if you have any questions or comments.


```{note}
Squishy does not have an official discord, nor any endorsed discord servers, for an explanation as to why, see the [F.A.Q.]
```
[sniff, analyze, and replay SCSI bus traffic]: ./applets/analyzer.md
[boot a modern system from 9-track tape]: ./applets/taperipper.md
[gateware]: ./library/gateware/index.md
[python]: ./library/python/index.md
[hardware]: ./hardware/index.md
[powerful applet system]: ./applets/index.md
[Introduction]: ./introduction.md
[Getting Started]: ./getting_started.md
[GitHub]: https://github.com/squishy-scsi/squishy
[Squishy]: https://github.com/squishy-scsi/squishy
[BlueSCSI]: https://scsi.blue/
[SCSI2SD]: https://www.codesrc.com/mediawiki/index.php/SCSI2SD
[PiSCSI]: https://github.com/PiSCSI/piscsi
[#squishy on libera.chat]: https://web.libera.chat/#squishy
[GitHub Discussions]: https://github.com/squishy-scsi/squishy/discussions
[F.A.Q.]: ./faq.md
