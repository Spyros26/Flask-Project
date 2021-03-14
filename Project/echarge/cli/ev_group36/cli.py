import os
import click
import importlib


class ComplexCLI(click.MultiCommand):
    def list_commands(self, ctx):
        commands = []
        commands_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))
        for filename in os.listdir(commands_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                commands.append(filename.replace("cmd_", "").replace(".py", ""))

        commands.sort()
        return commands

    def get_command(self, ctx, name):
        try:
            print(1)
            mod = __import__(f"ev_group36.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            print(2)
            return
        return mod.cli


@click.command(cls=ComplexCLI)
def cli():
    """Welcome to ev_group36!"""
    pass