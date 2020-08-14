from gi.repository import GLib, Wnck


class WindowSpy:
    def __init__(self, print_window_info, verbose, no_actions):
        self._print_window_info = print_window_info
        self._verbose = verbose
        self._no_actions = no_actions

        self._screen = Wnck.Screen.get_default()
        self._screen.connect("window-opened", self._on_window_opened)

    def _print_info(self, window):
        print("New window")
        print(' name:\t\t"{}"'.format(window.get_name()))
        print(' class_group:\t"{}"'.format(window.get_class_group_name()))
        print(' role:\t\t"{}"'.format(window.get_role()))
        print(' app_name:\t"{}"'.format(window.get_application().get_name()))

    def _on_window_opened(self, screen, window):
        if self._print_window_info:
            self._print_info(window)
        if self._match_window(window):
            self._action(window, screen)

    def _match_window(self, window):
        if window.get_class_group_name() == "URxvt":
            return True

    def _action(self, window, screen):
        workspace = screen.get_workspace(1)
        if workspace:
            window.move_to_workspace(workspace)
            window.maximize()
            # Delay workspace switch or WM might be confused
            GLib.timeout_add(100, self._workspace_activate, workspace)

    def _workspace_activate(self, workspace):
        workspace.activate(0)
        return False
