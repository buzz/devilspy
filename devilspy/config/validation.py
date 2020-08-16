"""Validation for config object."""


def _validate_type(val, exp_type):
    """Ensure val is of type."""
    if isinstance(val, exp_type):
        return None
    return "Expected type {} (got {}).".format(exp_type.__name__, type(val).__name__)


def validate_int(val):
    """Ensure val is of type int."""
    return _validate_type(val, int)


def validate_bool(val):
    """Ensure val is of type bool."""
    return _validate_type(val, bool)
