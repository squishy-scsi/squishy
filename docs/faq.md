# Frequently Asked Questions

The following are some commonly asked questions, while this section is not exhaustive it will be updated when appropriate. For more specific questions, please join the IRC channel [#squishy on libera.chat] or use the [GitHub Discussions].


## Why should I use Squishy rather than one of the other SCSI projects?

That really depends on what you need. If you just want/need storage emulation, then please do go with one of the other projects, [BlueSCSI] et. al. are awesome projects and deserve your support.

But if you need something more flexible, or support for arcane hardware, then Squishy might be the right choice. It's not as turnkey as the other projects, but it is far more capable in more ways than one.


## Why is Squishy so complex?

Squishy, at first, seems overly complicated for what it is, after all, the other SCSI projects are fairly simple, not more than a handful of parts, where as Squishy is this monster with multiple boards, large power requirements and a complex software stack.

But it's for a good reason, Squishy was designed to be as capable, covering everything for SCSI-1 and HVD all the way to ULTRA-320 LVD, and everything between. Such capabilities demand complexity in order to be achieved, this is the primary driver behind the complexity of both the hardware and software ecosystem. However, this allows Squishy to be as flexible as possible, able to hopefully meet any possible needs that may arise.


## Why is Squishy so expensive?

This goes in tandem with [Why is Squishy so complex?](#why-is-squishy-so-complex). It is not expensive for the sake of being expensive, the upmost care and detail has been put in to the design, as such I like to say that Squishy is not built down to a price, but up to a standard, and that standard is very high.

This, unfortunately leads to the hardware being expensive, there is sadly nothing that can be done about that. However, as Squishy is 100% Open Source Hardware under the [CERN-OHL-S v2], you can go and build it yourself to try to cut down on costs. However, assembling Squishy yourself is not a trivial task due to several large BGA components and fairly tight tolerances for manufacturing.


## Why Does Squishy not have a Discord?

Squishy likes to do things out in the open, this means that Discords model of walled-off communities is not conducive to how we want to do things. In addition to this, there is a trend to moving documentation away from things like Wiki's and websites into Discord servers, which causes that information to no longer be publicly accessible, this is a huge problem when it comes to things like Open Source projects such as Squishy.

All in all, to make things easier on both the maintainers and community members, we are staying away from Discord for the forseeable future. We have an <a href="irc://irc.libera.chat:6667/#squishy">IRC chanel</a> for developer talk and general chatting, and for everything else we have the [GitHub Discussions], [Issue tracker], and this website.



[#squishy on libera.chat]: https://web.libera.chat/#squishy
[GitHub Discussions]: https://github.com/squishy-scsi/squishy/discussions
[Issue tracker]: https://github.com/squishy-scsi/squishy/issues
[BlueSCSI]: https://scsi.blue/
[CERN-OHL-S v2]: https://ohwr.org/cern_ohl_s_v2.pdf
