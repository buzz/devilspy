"""Command line interface."""

import logging
import os
import os.path
import sys

import click
from gi.repository import Gdk, GLib
import yaml

# from devilspy.logger import logger
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


def parse_config(_, __, value):
    """Validate config file."""
    return yaml.safe_load(value)


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
    "-p",
    "--print-window-info",
    is_flag=True,
    help="Print information about new windows.",
)
@click.option(
    "-d", "--debug", is_flag=True, help="Print debug messages.",
)
@click.option(
    "-n", "--no-actions", is_flag=True, help="Do not carry out any window actions.",
)
@click.option(
    "-d", "--daemon", is_flag=True, help="Fork into background.",
)
@click.option(
    "-c",
    "--config",
    callback=parse_config,
    default=default_config_file,
    show_default=True,
    help="Config file to load.",
    type=click.File("r"),
)
@click.version_option(VERSION)
def cli(config, print_window_info, debug, no_actions, daemon):
    """Instantiate and start an devilspy."""
    if daemon:
        pid = os.fork()
        if pid > 0:
            # parent process
            sys.exit(0)

    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    Gdk.init([])
    main_loop = GLib.MainLoop()

    try:
        WindowSpy(
            config, print_window_info, no_actions,
        )
        main_loop.run()
    except KeyboardInterrupt:
        main_loop.quit()
    except RuntimeError:
        logging.exception("Error encountered! Exiting...")
        sys.exit(-1)

    sys.exit(0)
