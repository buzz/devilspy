# pylint: disable=import-outside-toplevel

"""devilspy main entry point."""


def main():
    """Start devilspy."""
    import gi

    gi.require_version("Gdk", "3.0")
    gi.require_version("GLib", "2.0")
    gi.require_version("Gtk", "3.0")
    gi.require_version("Wnck", "3.0")

    from devilspy.cli import cli

    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli(auto_envvar_prefix="DEVILSPY")


if __name__ == "__main__":
    main()
