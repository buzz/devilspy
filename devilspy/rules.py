"""Window matching rules."""

import re

from devilspy.logger import main_logger

logger = main_logger.getChild("rules")


def check_rule(entry_name, i, rule, window):
    """Evaluate rule on window."""
    if "match" in rule:
        if rule["match"] == "exact":
            func_matcher = exact_string
        elif rule["match"] == "regex":
            func_matcher = regex_string
        elif rule["match"] == "substring":
            func_matcher = substring_string

        result = func_matcher(rule["val"], get_window_data(window, rule["field"]))
        logger.debug("entry=%s match=%s rule=#%d %s", entry_name, result, i, rule)
        return result

    return False


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


def substring_string(match_strings, value):
    """Check for substring in string."""
    for string in match_strings:
        if string in value:
            return True
    return False
