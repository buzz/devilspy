"""Main devilspy manager object lives here."""

from gi.repository import Wnck

from devilspy.actions import perform_actions
from devilspy.logger import logger
from devilspy.rules import check_rule


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
        for entry_name in self._config:
            logger.debug('Trying entry "%s"', entry_name)

            try:
                matchers = self._config[entry_name]["rules"]
            except KeyError:
                logger.warning('Missing key "rules" for entry "%s"!', entry_name)
                return
            try:
                actions = self._config[entry_name]["actions"]
            except KeyError:
                logger.warning('Missing key "actions" for entry "%s"!', entry_name)
                return

            if any(check_rule(rule, arg, window) for rule, arg in matchers.items()):
                logger.debug('Entry "%s" matched', entry_name)
                perform_actions(entry_name, actions, window, screen)
