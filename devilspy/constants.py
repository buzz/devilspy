"""Rule and action definitions."""

from devilspy.config.validation import validate_bool, validate_int

ACTION_ARG_VALIDATORS = {
    "workspace": validate_int,
    "maximize": validate_bool,
    "activate_workspace": validate_int,
}
ALLOWED_ACTIONS = ACTION_ARG_VALIDATORS.keys()

RULE_NAMES = ("exact", "regex", "substring")
FIELD_NAMES = ("class_group", "name", "role", "app_name")
