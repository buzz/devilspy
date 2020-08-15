"""Window matching rules."""

import re

from devilspy.logger import logger

ALLOWED_STRING_RULES = ("exact", "match", "regex")
ALLOWED_STRING_FIELDS = ("class_group", "name", "role", "app_name")


class InvalidRuleError(ValueError):
    """Raised when a rule could not be parsed."""

    def __init__(self, message):
        super().__init__()
        self.message = message


def check_rule(name, arg, window):
    """Evaluate rule on window."""
    try:
        # string matchers
        if name in ALLOWED_STRING_RULES:
            field, val = get_field_val(arg)
            if name == "exact":
                func_matcher = exact_string
            elif name == "match":
                func_matcher = match_string
            elif name == "regex":
                func_matcher = regex_string

        # shortcut syntax for exact_string
        elif name in ALLOWED_STRING_FIELDS:
            field = name
            val = arg
            func_matcher = exact_string

        else:
            raise InvalidRuleError('Unknown rule name: "{}"'.format(name))

        # check field
        if not isinstance(field, str):
            raise InvalidRuleError('Argument "field" must be string.')
        # check val
        if isinstance(val, str):
            val = (val,)
        elif not (isinstance(val, list) and all(isinstance(item, str) for item in val)):
            raise InvalidRuleError('Argument "val" must be string or list of strings.')

        result = func_matcher(val, get_window_data(window, field))
        logger.debug("Result=%s rule_name=%s args=%s", result, name, arg)
        return result

    except InvalidRuleError as error:
        logger.warning('Invalid rule "%s": %s: %s', name, error.message, arg)
    return False


def get_field_val(arg):
    """Exctract field and value from rule argument."""
    try:
        field, val = arg["field"], arg["val"]
    except KeyError:
        raise InvalidRuleError("Rule argument must have field and val keys.")
    except TypeError:
        raise InvalidRuleError("Rule argument must be dict.")
    return field, val


def get_window_data(window, field):
    """Extract piece of information from window."""
    if field == "class_group":
        return window.get_class_group_name()
    if field == "name":
        return window.get_name()
    if field == "role":
        return window.get_role()
    if field == "app_name":
        return window.get_application().get_name()
    raise InvalidRuleError(
        'Invalid field: "{}", must be one of {}'.format(field, ALLOWED_STRING_FIELDS)
    )


def exact_string(match_strings, value):
    """Check for exact string equality."""
    for string in match_strings:
        if string == value:
            return True
    return False


def regex_string(regexes, value):
    """Check for regex matching string."""
    for regex in regexes:
        if re.search(regex, value):
            return True
    return False


def match_string(match_strings, value):
    """Check for substring in string."""
    for string in match_strings:
        if string in value:
            return True
    return False
