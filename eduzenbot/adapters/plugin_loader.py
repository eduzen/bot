import importlib.util
import inspect
from pathlib import Path

import logfire
from telegram.ext import CommandHandler


def _get_commands_path() -> Path:
    """Get the absolute path to the commands directory."""
    return Path(__file__).resolve().parent / ".." / "plugins" / "commands"


def _get_plugin_folders(commands_path: Path) -> list[Path]:
    """Retrieve all plugin folders containing a command.py file."""
    return [folder for folder in commands_path.iterdir() if (folder / "command.py").is_file()]


def _load_module_from_folder(folder_path: Path) -> None | object:
    """Dynamically load the command.py module from a given plugin folder."""
    module_name = f"eduzenbot.plugins.commands.{folder_path.name}.command"
    command_file = folder_path / "command.py"

    try:
        spec = importlib.util.spec_from_file_location(module_name, command_file)
        module = importlib.util.module_from_spec(spec)
        logfire.debug(f"Loading module {module_name} ...")
        spec.loader.exec_module(module)
        return module
    except Exception:
        logfire.exception(f"Error loading module {module_name}")
        return None


def _extract_command_handlers(module, module_name: str, registered_commands: set) -> list[CommandHandler]:
    """
    Extract CommandHandler instances from a module using docstring definitions.

    Args:
        module: The imported module.
        module_name: The plugin folder name.
        registered_commands: A set of already registered command names.

    Returns:
        List[CommandHandler]: CommandHandlers ready to be registered.
    """
    handlers: list[CommandHandler] = []
    if not module.__doc__:
        logfire.warn(f"Module {module_name} has no docstring. Skipping...")
        return handlers

    for line in module.__doc__.strip().splitlines():
        parts = [s.strip().lower() for s in line.split("-")]
        if len(parts) != 2:
            logfire.warn(f"Invalid docstring format in {module_name}: {line}")
            continue
        command_name, func_name = parts

        if command_name in registered_commands:
            logfire.warn(f"Duplicate command /{command_name} detected. Skipping...")
            continue

        func = getattr(module, func_name, None)
        if func and inspect.isfunction(func):
            handlers.append(CommandHandler(command_name, func))
            registered_commands.add(command_name)
            logfire.info(f"Registered command: /{command_name} -> {module_name}.{func_name}")
        else:
            logfire.warn(f"Function '{func_name}' not found in {module_name}")

    return handlers


def load_and_register_plugins() -> list[CommandHandler]:
    """
    Load plugin commands from the plugins directory and register them.

    Returns:
        List[CommandHandler]: A list of registered CommandHandler instances.
    """
    logfire.info("Loading plugins...")
    handlers = []
    registered_commands: set[str] = set()
    commands_path = _get_commands_path()

    for folder_path in _get_plugin_folders(commands_path):
        module = _load_module_from_folder(folder_path)
        if not module:
            continue

        module_handlers = _extract_command_handlers(module, folder_path.name, registered_commands)
        handlers.extend(module_handlers)

    logfire.info(f"Handlers created: {handlers}")
    return handlers
