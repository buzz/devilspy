from time import sleep
from gi.repository import Wnck


class WindowSpy:
    def __init__(self, debug=False):
        self._debug = debug
        self._screen = Wnck.Screen.get_default()
        self._screen.connect("window-opened", self._on_window_opened)

    def _print_debug(self, name, class_group, role, app_name):
        print("new window")
        print(" name:", name)
        print(" class group name:", class_group)
        print(" role:", role)
        print(" application name:", app_name)

    def _on_window_opened(self, screen, window):
        name = window.get_name()
        class_group = window.get_class_group_name()
        role = window.get_role()
        app_name = window.get_application().get_name()

        if self._debug:
            self._print_debug(name, class_group, role, app_name)

        if class_group == "URxvt":
            workspace = screen.get_workspace(1)
            if workspace:
                window.move_to_workspace(workspace)
                window.maximize()
                sleep(0.1)
                workspace.activate(0)
