"""Main devilspy manager object lives here."""

from gi.repository import Wnck

from devilspy.actions import perform_actions
from devilspy.logger import main_logger
from devilspy.rules import check_rule

window_logger = main_logger.getChild("window")
logger = main_logger.getChild("spy")


class WindowSpy:
    """Hook into new events, match windows and carry out custom actions."""

    def __init__(self, config, print_window_info, no_actions):
        self._config = config
        self._print_window_info = print_window_info
        self._no_actions = no_actions

        self._screen = Wnck.Screen.get_default()
        self._screen.connect("window-opened", self._on_window_opened)

    def _print_info(self, window):
        window_logger.info('  name:\t\t"%s"', window.get_name())
        window_logger.info('  class_group:\t"%s"', window.get_class_group_name())
        window_logger.info('  role:\t\t"%s"', window.get_role())
        window_logger.info('  app_name:\t"%s"', window.get_application().get_name())

    def _on_window_opened(self, screen, window):
        if self._print_window_info:
            self._print_info(window)
        self._match_window(window, screen)

    def _match_window(self, window, screen):
        for entry_name in self._config.entries:
            logger.debug('Trying entry "%s"', entry_name)
            matchers = self._config.entries[entry_name]["rules"]
            if any(check_rule(rule, arg, window) for rule, arg in matchers.items()):
                actions = self._config.entries[entry_name]["actions"]
                perform_actions(entry_name, actions, window, screen)
