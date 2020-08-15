"""Main devilspy manager object lives here."""

from gi.repository import GLib, Wnck

from devilspy.logger import logger


class MatchFound(Exception):
    """Raised when a window matches and actions should be performed."""


class WindowSpy:
    """Hook into new events, match windows and carry out custom actions."""

    def __init__(self, config, print_window_info, no_actions):
        self._config = config
        self._print_window_info = print_window_info
        self._no_actions = no_actions

        self._screen = Wnck.Screen.get_default()
        self._screen.connect("window-opened", self._on_window_opened)

    def _print_info(self, window):
        logger.info("New window")
        logger.info('  name:\t\t"%s"', window.get_name())
        logger.info('  class_group:\t"%s"', window.get_class_group_name())
        logger.info('  role:\t\t"%s"', window.get_role())
        logger.info('  app_name:\t"%s"', window.get_application().get_name())

    def _on_window_opened(self, screen, window):
        if self._print_window_info:
            self._print_info(window)
        self._match_window(window, screen)

    def _match_window(self, window, screen):
        for entry in self._config:
            logger.debug('Trying entry "%s"', entry)

            try:
                matchers = self._config[entry]["match"]
            except KeyError:
                logger.warning('Missing key "match" for entry "%s"!', entry)
                return
            try:
                actions = self._config[entry]["actions"]
            except KeyError:
                logger.warning('Missing key "actions" for entry "%s"!', entry)
                return

            try:
                for matcher in matchers:
                    val = matchers[matcher]
                    if matcher == "class_group_name":
                        vals = val if isinstance(val, list) else (val,)
                        for test_str in vals:
                            if window.get_class_group_name() == test_str:
                                raise MatchFound()
            except MatchFound:
                logger.debug('Entry "%s" matched', entry)
                self._action(entry, actions, window, screen)

    def _action(self, entry, actions, window, screen):
        for action in actions:
            action_arg = actions[action]

            if action == "workspace":
                logger.debug('Action "%s": Move to workspace %d', entry, action_arg)
                workspace_num = int(action_arg)
                workspace = screen.get_workspace(workspace_num)
                if workspace:
                    if workspace != window.get_workspace():
                        window.move_to_workspace(workspace)

            elif action == "maximize":
                logger.debug('Action "%s": Maximize', entry)
                if action_arg:
                    if not window.is_maximized():
                        window.maximize()
                else:
                    if window.is_maximized():
                        window.unmaximize()

            elif action == "activate_workspace":
                logger.debug('Action "%s": Activate workspace %d', entry, action_arg)
                workspace_num = int(action_arg)
                workspace = screen.get_workspace(workspace_num)
                if workspace:
                    if workspace != screen.get_active_workspace():
                        # Delay workspace switch or some window managers have display issues
                        GLib.timeout_add(100, self._workspace_activate, workspace)

            else:
                logger.warning('Unknown action for "%s": %s', entry, action)

    def _workspace_activate(self, workspace):
        workspace.activate(0)
        return False
