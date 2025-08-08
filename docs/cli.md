# CLI

```{todo}
Flesh this section out
```

The Squishy CLI is the primary way to interact with Squishy and Squishy devices, you can interact with them [programmatically], but that is not expected from end users of Squishy devices.

When driving the Squishy CLI, there are two primary ways of invoking it, they depend if you have installed Squishy to your system (simply running `squishy` as the command) or are operating it out of the git repository (running it as `python -m squishy`). We will assume the former and use the main invocation as only `squishy`, but they are both valid.

As an example, to get the current version of the Squishy software, you can run:

```
$ squishy -V
```

Squishy CLI invocations usually follow the the following pattern:

```
$ squishy [-v] [-d DEVICE] <ACTION> args...
```

Where `-v` is for verbose/debug logging, `-d DEVICE` is a specified Squishy hardware device, and `<ACTION> args...`  is the thing you are trying to do and it's arguments.

If you only have one hardware Squishy device attached to your system, you can omit `-d DEVICE` from most if not all commands, as it will automatically be detected and used if needed.

## Shell Completions

We maintain a [zsh] shell [completion provider] that can be installed by copying the `contrib/squishy-completion.zsh` into the directory where your zsh completions are stored under the name `_squishy`. This will allow for full tab-completion of the Squishy CLI, including device selection.

[programmatically]: ./library/applet/device.md
[zsh]: https://www.zsh.org/
[completion provider]: https://github.com/squishy-scsi/squishy/blob/main/contrib/squishy-completion.zsh
