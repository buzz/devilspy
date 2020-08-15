"""Window actions."""

from gi.repository import GLib

from devilspy.logger import main_logger

logger = main_logger.getChild("actions")


def perform_actions(entry_name, actions, window, screen):
    """Perform set of actions on window."""
    for action, arg in actions.items():

        if action == "workspace":
            workspace(arg, entry_name, window, screen)

        elif action == "maximize":
            logger.debug('Action "%s": Maximize', entry_name)
            if arg:
                if not window.is_maximized():
                    window.maximize()
            else:
                if window.is_maximized():
                    window.unmaximize()

        elif action == "activate_workspace":
            logger.debug('Action "%s": Activate workspace %d', entry_name, arg)
            workspace_num = int(arg)
            space = screen.get_workspace(workspace_num)
            if space:
                if space != screen.get_active_workspace():
                    # Delay workspace switch or some window managers have display issues
                    GLib.timeout_add(100, delayed_activate_workspace, space)

        else:
            logger.warning('Unknown action for "%s": %s', entry_name, action)


def workspace(arg, entry_name, window, screen):
    """Move window to another workspace."""
    logger.debug('Action "%s": Move to workspace %d', entry_name, arg)
    workspace_num = int(arg)
    space = screen.get_workspace(workspace_num)
    if space:
        if space != window.get_workspace():
            window.move_to_workspace(space)


def delayed_activate_workspace(space):
    """Delayed workspace switch."""
    space.activate(0)
    return False
