"""Window matching."""

from devilspy.logger import logger


def match(rule, arg, window):
    """Evaluate rule on window."""
    if rule == "class_group":
        return exact_string(arg, window.get_class_group_name())

    logger.warning('Encountered unknown rule "%s"', rule)
    return False


def exact_string(arg, expected_string):
    """Check for exact string equality."""
    args = arg if isinstance(arg, list) else (arg,)
    for teststring in args:
        if teststring == expected_string:
            return True
    return False
