"""Window actions."""

from gi.repository import GLib

from devilspy.logger import main_logger

logger = main_logger.getChild("actions")


def perform_actions(entry_name, actions, window, screen):
    """Perform set of actions on window."""
    for i, action in enumerate(actions):
        logger.debug(
            "Entry %s: #%d %s %s", entry_name, i, action["name"], action["arg"]
        )
        action_func = getattr(Actions, action["name"])
        action_func(action["arg"], window, screen)


class Actions:
    """Implementation of window actions."""

    @staticmethod
    def workspace(workspace_num, window, screen):
        """Move window to another workspace."""
        space = screen.get_workspace(int(workspace_num))
        if space and space != window.get_workspace():
            window.move_to_workspace(space)

    @staticmethod
    def maximize(do_maximize, window, _):
        """(Un)maximize window."""
        if do_maximize:
            if not window.is_maximized():
                window.maximize()
        else:
            if window.is_maximized():
                window.unmaximize()

    @classmethod
    def activate_workspace(cls, workspace_num, _, screen):
        """Switch workspace."""
        space = screen.get_workspace(int(workspace_num))
        if space and space != screen.get_active_workspace():
            # Delay workspace switch or some window managers have display issues
            GLib.timeout_add(100, cls._delayed_activate_workspace, space)

    @staticmethod
    def _delayed_activate_workspace(space):
        """Delayed workspace switch."""
        space.activate(0)
        return False
