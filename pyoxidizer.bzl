# SPDX-License-Identifier: BSD-3-Clause
# This is the configuration file for the Windows and macOS builds of
# squishy done via PyOxidizer.

PYTHON_VERSION = '3.9'

def init_policy(dist):
    policy = dist.make_python_packaging_policy()

    policy.include_distribution_resources = True
    policy.allow_in_memory_shared_library_loading = True
    policy.allow_files = True
    policy.extension_module_filter = 'all'

    return policy

def init_config(dist):
    config = dist.make_python_interpreter_config()
    config.config_profile = 'python'

    config.module_search_paths = [
        '$ORIGIN/lib',
    ]

    return config

def install_deps(executable):
    for res in executable.pip_install(['.']):
        executable.add_python_resource(res)


def init_dist(dist):
    policy = init_policy(dist)
    config = init_config(dist)

    executable = dist.to_python_executable(
        name             = 'squishy',
        packaging_policy = policy,
        config           = config
    )


    install_deps(executable)


    return executable

def init_resources(executable):
    return executable.to_embedded_resources()

def init_install(exe):
    # Create an object that represents our installed application file layout.
    files = FileManifest()

    # Add the generated executable to our install layout in the root directory.
    files.add_python_resource(".", exe)

    return files

def init_msi(executable):
    return executable.to_wix_msi_builder(
        'squishy',
        'Squishy',
        '0.1',
        'Aki \'lethalbit\' Van Ness'
    )

def init_linux():
    dist = default_python_distribution(
        flavor         = 'standalone_dynamic',
        build_target   = 'x86_64-unknown-linux-gnu',
        python_version = PYTHON_VERSION,
    )

    return init_dist(dist)


def init_windows():
    dist = default_python_distribution(
        flavor         = 'standalone_dynamic',
        build_target   = 'x86_64-pc-windows-msvc',
        python_version = PYTHON_VERSION,
    )

    return init_dist(dist)

def init_macos_arm():
    dist = default_python_distribution(
        flavor         = 'standalone_dynamic',
        build_target   = 'aarch64-apple-darwin',
        python_version = PYTHON_VERSION,
    )

    return init_dist(dist)

def init_macos_x86():
    dist = default_python_distribution(
        flavor         = 'standalone_dynamic',
        build_target   = 'x86_64-apple-darwin',
        python_version = PYTHON_VERSION,
    )

    return init_dist(dist)


def register_linux():
    register_target(
        'x86_64-unknown-linux-gnu-exec',
        init_linux
    )

    register_target(
        'x86_64-unknown-linux-gnu-res',
        init_resources,
        depends = [
            'x86_64-unknown-linux-gnu-exec'
        ],
        default_build_script = True
    )

    register_target(
        'x86_64-unknown-linux-gnu-install',
        init_install,
        depends = [
            'x86_64-unknown-linux-gnu-exec'
        ],
        default = True
    )

def register_windows():
    register_target(
        'x86_64-pc-windows-msvc-exec',
        init_windows
    )

    register_target(
        'x86_64-pc-windows-msvc-res',
        init_resources,
        depends = [
            'x86_64-pc-windows-msvc-exec'
        ],
        default_build_script = True
    )

    register_target(
        'x86_64-pc-windows-msvc-install',
        init_install,
        depends = [
            'x86_64-pc-windows-msvc-exec'
        ],
        default = True
    )

    register_target(
        'x86_64-pc-windows-msvc-msi',
        init_msi,
        depends = [
            'x86_64-pc-windows-msvc-exec'
        ],
    )

def register_macos():
    register_target(
        'aarch64-apple-darwin-exec',
        init_macos_arm
    )

    register_target(
        'x86_64-apple-darwin-exec',
        init_macos_x86
    )

    register_target(
        'aarch64-apple-darwin-res',
        init_resources,
        depends = [
            'aarch64-apple-darwin-exec'
        ],
        default_build_script = True
    )

    register_target(
        'aarch64-apple-darwin-install',
        init_install,
        depends = [
            'aarch64-apple-darwin-exec'
        ],
        default = True
    )

    register_target(
        'x86_64-apple-darwin-res',
        init_resources,
        depends = [
            'x86_64-apple-darwin-exec'
        ],
        default_build_script = True
    )

    register_target(
        'x86_64-apple-darwin-install',
        init_install,
        depends = [
            'x86_64-apple-darwin-exec'
        ],
        default = True
    )

def init_targets():
    register_linux()
    register_windows()
    register_macos()


init_targets()
resolve_targets()
