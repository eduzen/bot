# eduzenbot/adapters/plugin_loader.py

import os
import pkgutil
from collections.abc import Callable
from typing import Any

import logfire


def get_commands_from_plugin(plugin) -> dict[str, Callable]:
    """
    Each plugin should document commands in its __doc__ with lines like:
        command_name - function_name
    """
    plugins: dict[str, Callable] = {}
    if not plugin.__doc__:
        return plugins

    for line in plugin.__doc__.strip().splitlines():
        command = [s.strip() for s in line.split("-")]
        cmd_name, func_name = command[0], command[1]
        plugins[cmd_name] = getattr(plugin, func_name)
    return plugins


def find_modules(paths: list[str]) -> dict[str, Any]:
    commands = {}
    for importer, package_name, _ in pkgutil.iter_modules(paths):
        plugin = importer.find_module(package_name).load_module(package_name)
        commands.update(get_commands_from_plugin(plugin))
    return commands


def load_plugins(plugins_root: str) -> dict[str, Callable]:
    """
    Recursively loads modules from the given folder,
    aggregating commands declared in their __doc__.
    """
    logfire.info(
        f"Loading plugins from {plugins_root}...",
    )
    all_commands = {}
    for importer, package_name, _ in pkgutil.iter_modules([plugins_root]):
        logfire.info(f"Loading {package_name} ...")
        sub_modules = os.path.join(plugins_root, package_name)
        importer.find_module(package_name).load_module(package_name)  # type: ignore
        commands = find_modules([sub_modules])
        all_commands.update(commands)

    logfire.info(f"Found {len(all_commands)} commands in total")
    return all_commands
