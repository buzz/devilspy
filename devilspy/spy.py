"""Main devilspy manager object lives here."""

from gi.repository import Wnck

from devilspy.logger import main_logger

window_logger = main_logger.getChild("window")


class WindowSpy:
    """Hook into new events, match windows and carry out custom actions."""

    def __init__(self, config, print_window_info, no_actions):
        self._config = config
        self._print_window_info = print_window_info
        self._no_actions = no_actions

        self._screen = Wnck.Screen.get_default()
        self._screen.connect("window-opened", self.on_window_opened)

    def on_window_opened(self, screen, window):
        """Callback for new windows."""
        if self._print_window_info:
            WindowSpy._print_info(window)
        self.match_window(window, screen)

    def match_window(self, window, screen):
        """Match window agains all entries in configuration."""
        for entry in self._config.entries:
            if entry.match(window):
                entry.run_actions(window, screen, dry_run=self._no_actions)

    @staticmethod
    def _print_info(window):
        window_logger.info("  name:        '%s'", window.get_name())
        window_logger.info("  class_group: '%s'", window.get_class_group_name())
        window_logger.info("  role:        '%s'", window.get_role())
        window_logger.info("  app_name:    '%s'", window.get_application().get_name())
