"""Command line interface."""

import logging
import os
import os.path
import sys

import click
from gi.repository import Gdk, GLib

from devilspy.config import Config
from devilspy.logger import main_logger
from devilspy.meta import DESCRIPTION, PROGRAM_NAME, WEBSITE, VERSION
from devilspy.spy import WindowSpy

EPILOG = """{}

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
"""

config_home = GLib.get_user_config_dir()
default_config_file = os.path.join(config_home, PROGRAM_NAME, "config.yml")


def get_epilog():
    """Format custom epilog."""
    return EPILOG.format(WEBSITE)


def parse_config(_, __, filepath):
    """Parse YAML config file."""
    return Config.load_yaml_file(filepath)


def cb_print_window_info(ctx, param, print_window_info):
    """Enable if debug is set."""
    try:
        if ctx.params["debug"] and not print_window_info:
            main_logger.info("Enabling --print-window-info because --debug is true.")
            return True
    except KeyError:
        pass
    return print_window_info


class CustomEpilogCommand(click.Command):
    """Format epilog in a custom way."""

    def format_epilog(self, _, formatter):
        """Format epilog while preserving newlines."""
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write_text(line)


@click.command(cls=CustomEpilogCommand, help=DESCRIPTION, epilog=get_epilog())
@click.option(
    "-c",
    "--config",
    callback=parse_config,
    default=default_config_file,
    show_default=True,
    help="Config file to load.",
    type=click.Path(dir_okay=False),
)
@click.option("-f", "--fork", is_flag=True, help="Fork into background.")
@click.option(
    "-n", "--no-actions", is_flag=True, help="Do not carry out any window actions."
)
@click.option(
    "-p",
    "--print-window-info",
    callback=cb_print_window_info,
    is_flag=True,
    help="Print information about new windows.",
)
@click.option("-d", "--debug", is_flag=True, help="Print debug messages.")
@click.version_option(VERSION)
def cli(config, fork, no_actions, print_window_info, debug):
    """Instantiate and start an devilspy."""
    if fork:
        pid = os.fork()
        if pid > 0:
            # parent process
            sys.exit(0)

    if debug:
        main_logger.setLevel(logging.DEBUG)

    Gdk.init([])
    main_loop = GLib.MainLoop()

    try:
        WindowSpy(
            config, print_window_info, no_actions,
        )
        main_loop.run()
    except KeyboardInterrupt:
        main_loop.quit()

    sys.exit(0)
