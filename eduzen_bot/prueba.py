from glob import glob
import pkgutil
import importlib
import imp
import os

command_folder = "./plugins/commands"
main_package = "__init__"
command = "command"


def get_plugins():
    plugins = []
    possibleplugins = os.listdir(command_folder)
    for i in possibleplugins:
        location = os.path.join(command_folder, i)
        # location = os.path.join(location, 'command')
        if not os.path.isdir(location) or not main_package + ".py" in os.listdir(
            location
        ):
            continue

        if f"{command}.py" not in os.listdir(location):
            continue

        info = imp.find_module(command, [location])
        plugins.append({"name": i, "info": info})
    return plugins


def load_plugin(plugin):
    return imp.load_module(command, *plugin["info"])


def something():
    plugins_path = glob("plugins/*/*")
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins/commands")
    print(p)
    """
    a = {
        name: importlib.import_module(name)
        for finder, name, ispkg in pkgutil.iter_modules()
        if name.startswith('plugin')
    }
    """

    for name in plugins_path:
        if os.path.isdir(name) and "pycache" not in name:
            print(f"is dir: {name}")

    print("--")
    d = {}
    for finder, name, ispkg in pkgutil.iter_modules([p]):
        if ispkg:
            d[name] = importlib.import_module(name)

    print(d)


for plugin in get_plugins():
    print(f'Loading plugin {plugin["name"]}')
    p = load_plugin(plugin)
    import pdb

    pdb.set_trace()

    commands = [line.split("-") for line in p.__doc__.strip().splitlines()]
    print(commands)

print(2)
