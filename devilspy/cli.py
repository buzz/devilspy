"""Command line interface."""

import logging
import os
import sys

import click
from gi.repository import Gdk, GLib

from devilspy.meta import DESCRIPTION, WEBSITE, VERSION
from devilspy.spy import WindowSpy

EPILOG = """{}

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
"""


def _get_epilog():
    return EPILOG.format(WEBSITE)


class CustomEpilogCommand(click.Command):
    """Format epilog in a custom way."""

    def format_epilog(self, _, formatter):
        """Format epilog while preserving newlines."""
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write_text(line)


@click.command(cls=CustomEpilogCommand, help=DESCRIPTION, epilog=_get_epilog())
@click.option(
    "-p",
    "--print-window-info",
    is_flag=True,
    help="Print information about new windows.",
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Print actions taken for matching windows.",
)
@click.option(
    "-n", "--no-actions", is_flag=True, help="Do not carry out any window actions.",
)
@click.option(
    "-d", "--daemon", is_flag=True, help="Fork into background.",
)
@click.version_option(VERSION)
def cli(print_window_info, verbose, no_actions, daemon):
    """Instantiate and start an devilspy."""
    if daemon:
        pid = os.fork()
        if pid > 0:
            # parent process
            sys.exit(0)

    Gdk.init([])
    main_loop = GLib.MainLoop()

    try:
        WindowSpy(
            print_window_info=print_window_info, verbose=verbose, no_actions=no_actions
        )
        main_loop.run()
    except KeyboardInterrupt:
        main_loop.quit()
    except RuntimeError:
        logging.exception("Error encountered! Exiting...")
        sys.exit(-1)

    sys.exit(0)
