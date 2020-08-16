"""Configuration entry holding a set of rules and actions."""

from devilspy.config.actions import AbstractBaseAction
from devilspy.config.errors import (
    InvalidActionError,
    InvalidEntryError,
    InvalidRuleError,
)
from devilspy.config.abc import AbstractBaseConfigEntity
from devilspy.config.rules import AbstractBaseRule
from devilspy.logger import main_logger

logger = main_logger.getChild("config.entry")


class Entry(AbstractBaseConfigEntity):
    """
    A configuration constists of a number of entries.

    Each entry has a list of window matching rules and window actions.
    """

    _keys = {
        "actions": AbstractBaseAction,
        "rules": AbstractBaseRule,
    }

    def __init__(self, name):
        self.name = name
        self.actions = []
        self.rules = []

    def parse(self, data):
        for key, item_class in self._keys.items():
            for idx, item_data in enumerate(data[key]):
                try:
                    item = item_class.create(item_data, idx)
                    getattr(self, key).append(item)
                except InvalidActionError as error:
                    logger.warning("Invalid action: '%s' %s", self.name, error.message)
                except InvalidRuleError as error:
                    logger.warning("Invalid rule: '%s': %s", self.name, error.message)

    @classmethod
    def validate(cls, data):
        for key in cls._keys:
            try:
                if not isinstance(data[key], list):
                    raise InvalidEntryError("Type of '{}' must be list!".format(key))
            except KeyError:
                raise InvalidEntryError("Missing key '{}'!".format(key))
        return data

    def match(self, window):
        """Match entry against window."""
        for rule in self.rules:
            if rule.match(window):
                logger.debug("'%s' matched.", self.name)
                return True
        return False

    def run_actions(self, window, screen, dry_run=False):
        """Run all entry actions on window."""
        for action in self.actions:
            logger.debug(
                "Entry '%s': Action (%d) '%s' %s",
                self.name,
                action.idx,
                action.name,
                action.arg,
            )
            if not dry_run:
                action.run(window, screen)
