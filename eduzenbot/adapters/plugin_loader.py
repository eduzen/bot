import importlib.util
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


def load_module_from_path(module_name: str, path: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_modules(paths: list[str]) -> dict[str, Any]:
    commands = {}
    for path in paths:
        for _, package_name, _ in pkgutil.iter_modules([path]):
            module_path = os.path.join(path, f"{package_name}.py")
            module = load_module_from_path(package_name, module_path)
            commands.update(get_commands_from_plugin(module))
    return commands


def load_plugins(plugins_root: str) -> dict[str, Callable]:
    """
    Recursively loads modules from the given folder,
    aggregating commands declared in their __doc__.
    """
    logfire.info(f"Loading plugins from {plugins_root}...")
    all_commands = {}
    for importer, package_name, is_pkg in pkgutil.iter_modules([plugins_root]):
        # Skip packages and test directories
        if is_pkg or package_name == "tests":
            continue

        module_path = os.path.join(plugins_root, package_name)
        logfire.debug(f"Checking {module_path} ...")
        if not os.path.isfile(module_path):  # Ensure the module file exists
            logfire.warning(f"Module {module_path} does not exist")
            continue

        logfire.info(f"Loading {package_name} ...")
        commands = find_modules([module_path])
        all_commands.update(commands)

    logfire.info(f"Found {len(all_commands)} commands in total")
    return all_commands
