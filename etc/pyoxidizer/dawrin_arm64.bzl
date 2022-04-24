# SPDX-License-Identifier: BSD-3-Clause

PYTHON_VERSION = '3.8'

def init_policy(dist):
    policy = dist.make_python_packaging_policy()

    policy.include_distribution_resources = True
    policy.allow_in_memory_shared_library_loading = True
    policy.allow_files = True
    policy.resources_location_fallback = 'filesystem-relative:lib'
    policy.extension_module_filter = 'all'

    return policy

def init_config(dist):
    config = dist.make_python_interpreter_config()
    config.config_profile = 'isolated'
    config.run_module = 'squishy'

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

def init_dawrin_arm64():
    dist = default_python_distribution(
        flavor         = 'standalone_dynamic',
        build_target   = 'aarch64-apple-darwin',
        python_version = PYTHON_VERSION,
    )

    return init_dist(dist)

def register_darwin_arm64():
    register_target(
        'aarch64-apple-darwin-exec',
        init_darwin_arm64
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

register_darwin_arm64()
resolve_targets()
