# pylint: disable=import-outside-toplevel

"""devilspy main entry point."""


def main():
    """Start devilspy."""
    import gi

    gi.require_version("GLib", "2.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("Wnck", "3.0")
    from gi.repository import Gdk, GLib
    from devilspy.spy import WindowSpy

    Gdk.init([])
    main_loop = GLib.MainLoop()
    spy = WindowSpy(debug=True)

    try:
        main_loop.run()
    except KeyboardInterrupt:
        main_loop.quit()


if __name__ == "__main__":
    main()
