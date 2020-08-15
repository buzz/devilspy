"""Window matching rules."""

import re

from devilspy.logger import logger


def check_rule(name, arg, window):
    """Evaluate rule on window."""
    field, val = arg["field"], arg["val"]
    if name == "exact":
        func_matcher = exact_string
    elif name == "match":
        func_matcher = match_string
    elif name == "regex":
        func_matcher = regex_string

    result = func_matcher(val, get_window_data(window, field))
    logger.debug("match=%s rule_name=%s args=%s", result, name, arg)
    return result


def get_window_data(window, field):
    """Extract piece of information from window."""
    if field == "class_group":
        return window.get_class_group_name()
    if field == "name":
        return window.get_name()
    if field == "role":
        return window.get_role()
    # field == "app_name"
    return window.get_application().get_name()


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
