"""Window matcher rules."""

from abc import ABCMeta, abstractmethod
import re

from devilspy.config.abc import AbstractBaseConfigEnumerableEntity
from devilspy.config.errors import InvalidRuleError


class AbstractBaseRule(AbstractBaseConfigEnumerableEntity, metaclass=ABCMeta):
    """Abstract base class for window rules."""

    @classmethod
    def get_class_from_data(cls, data):
        try:
            name = data["match"]
        except (KeyError, TypeError):
            name = "exact"  # Short notation?
        return AbstractBaseStringMatcherRule.get_class_from_name(name)

    @classmethod
    def validate(cls, data):
        if not isinstance(data, dict):
            raise InvalidRuleError("Rule must be of type dict.")
        return data

    @abstractmethod
    def match(self, window):
        """Match rule against Wnck.Window."""


class AbstractBaseStringMatcherRule(AbstractBaseRule, metaclass=ABCMeta):
    """Abstract base class for string matcher rules."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = None
        self.val = None

    def parse(self, data):
        self.field = data["field"]
        self.val = data["val"]
        if isinstance(self.val, str):
            self.val = [self.val]  # Make sure val is a list

    @classmethod
    def validate(cls, data):
        data = super().validate(data)

        # Transform rule short notation into canonical form
        try:
            if len(data.keys()) == 1:
                field = list(data.keys())[0]
                data = {
                    "field": field,
                    "val": data[field],
                }
        except TypeError:
            pass

        # Check field
        if "field" not in data:
            raise InvalidRuleError("Missing 'field' key.")
        if data["field"] not in FIELD_NAMES:
            msg = "Value of 'field' must be one of {}.".format(FIELD_NAMES)
            raise InvalidRuleError(msg)

        # Check val
        if "val" not in data:
            raise InvalidRuleError("Missing 'val' key.")
        if isinstance(data["val"], str):
            return data
        if isinstance(data["val"], list) and all(
            isinstance(item, str) for item in data["val"]
        ):
            return data
        type_name = type(data["val"]).__name__
        msg = "'val' must be string or list of strings (got {}).".format(type_name)
        raise InvalidRuleError(msg)

    @classmethod
    def get_class_from_name(cls, name):
        """Get string matcher class for config name."""
        try:
            return STRING_RULE_MAPPING[name]
        except KeyError:
            vals = STRING_RULE_MAPPING.keys()
            raise InvalidRuleError(
                "Invalid value for 'match'. Must be one of {}.".format(vals)
            )

    def get_window_data(self, window):
        """Extract piece of information from window."""
        if self.field == "class_group":
            return window.get_class_group_name()
        if self.field == "name":
            return window.get_name()
        if self.field == "role":
            return window.get_role()
        return window.get_application().get_name()  # field == "app_name"


class ExactStringRule(AbstractBaseStringMatcherRule):
    """Match exact string equality."""

    name = "exact"

    def match(self, window):
        win_value = self.get_window_data(window)
        for value in self.val:
            if value == win_value:
                return True
        return False


class RegexRule(AbstractBaseStringMatcherRule):
    """Match regular expression against string."""

    name = "regex"

    def match(self, window):
        win_value = self.get_window_data(window)
        for regex in self.val:
            if re.search(regex, win_value):
                return True
        return False


class SubstringRule(AbstractBaseStringMatcherRule):
    """Match substring  against string."""

    name = "substring"

    def match(self, window):
        win_value = self.get_window_data(window)
        for string in self.val:
            if string in win_value:
                return True
        return False


FIELD_NAMES = ("class_group", "name", "role", "app_name")
STRING_RULE_CLASSES = (ExactStringRule, RegexRule, SubstringRule)
STRING_RULE_MAPPING = {cls.name: cls for cls in STRING_RULE_CLASSES}
