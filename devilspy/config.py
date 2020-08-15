"""devilspy configuration."""

import yaml

from devilspy.logger import main_logger

ALLOWED_STRING_RULES = ("exact", "match", "regex")
ALLOWED_STRING_FIELDS = ("class_group", "name", "role", "app_name")

logger = main_logger.getChild("config")


class Config:
    """Configuration class holds and validates rules."""

    def __init__(self, filepath):
        self._filepath = filepath
        config = self._parse_config()
        self.entries = Config._validate_config(config)

    def _parse_config(self):
        try:
            with open(self._filepath, "r") as configfile:
                return yaml.safe_load(configfile.read())
        except FileNotFoundError:
            logger.warning("Config file not found.")
        except yaml.scanner.ScannerError as error:
            logger.warning("Failed to parse config: %s", error)
        return {}

    @classmethod
    def _validate_config(cls, config):
        # config must be dict
        try:
            items = config.items()
        except AttributeError:
            logger.warning("Config should have a single dict of enries.")
            return False

        # validate entries
        entries = {}
        for name, entry in items:
            validated_entry = cls._validate_entry(name, entry)
            if validated_entry:
                entries[name] = validated_entry

        if len(entries.keys()) == 0:
            logger.warning("Using empty config.")

        return entries

    @classmethod
    def _validate_entry(cls, entry_name, entry):
        try:
            rules = entry["rules"]
        except KeyError:
            logger.warning('Missing key "rules" for entry "%s"!', entry_name)
            return None
        except TypeError:
            logger.warning('Key "rules" must be dict for entry "%s"!', entry_name)
            return None

        try:
            actions = entry["actions"]
        except KeyError:
            logger.warning('Missing key "actions" for entry "%s"!', entry_name)
            return None
        except TypeError:
            logger.warning('Key "actions" must be dict for entry "%s"!', entry_name)
            return None

        print(rules)
        rules_valid = dict(
            cls._validate_matcher(entry_name, name, arg) for name, arg in rules.items()
        )
        rules_valid = {name: arg for name, arg in rules_valid.items() if name and arg}

        actions_valid = dict(
            cls._validate_action(entry_name, name, arg) for name, arg in actions.items()
        )
        actions_valid = {
            name: arg for name, arg in actions_valid.items() if name and arg
        }

        return {"rules": rules_valid, "actions": actions_valid}

    @classmethod
    def _validate_matcher(cls, entry_name, name, arg):
        is_exact_string_shortcut_notation = name in ALLOWED_STRING_FIELDS
        is_string_matcher = name in ALLOWED_STRING_RULES

        if is_string_matcher or is_exact_string_shortcut_notation:

            # string matcher
            if is_string_matcher:
                validated_name, field, value = cls._validate_string_matcher_arg(
                    entry_name, name, arg
                )
                if validated_name is None:
                    return None, None

            # exact shortcut notation
            else:
                validated_name = "exact"
                field = name
                value = arg

            # value
            validated_value = cls._validate_string_matcher_value(value)
            if validated_value is None:
                cls._log_invalid_rule(
                    entry_name,
                    name,
                    arg,
                    'Argument "val" must be string or list of strings (got {}).'.format(
                        type(value).__name__
                    ),
                )
                return None, None

            return validated_name, {"field": field, "val": validated_value}

        cls._log_invalid_rule(entry_name, name, arg, "Invalid rule name.")
        return None, None

    @classmethod
    def _validate_string_matcher_arg(cls, entry_name, name, arg):
        validated_name = name

        try:
            field, value = arg["field"], arg["val"]
        except KeyError:
            cls._log_invalid_rule(
                entry_name,
                name,
                arg,
                'Rule argument must have keys "field" and "val".',
            )
            return None, None, None
        except TypeError:
            cls._log_invalid_rule(
                entry_name, name, arg, "Rule argument must be dict.",
            )
            return None, None, None

        # field
        if field not in ALLOWED_STRING_FIELDS:
            cls._log_invalid_rule(
                entry_name,
                name,
                arg,
                'Invalid field: "{}", must be one of {}.'.format(
                    field, ALLOWED_STRING_FIELDS
                ),
            )
            return None, None, None

        return validated_name, field, value

    @classmethod
    def _validate_string_matcher_value(cls, value):
        if isinstance(value, str):
            value = [value]
        elif not (
            isinstance(value, list) and all(isinstance(item, str) for item in value)
        ):
            return None
        return value

    @classmethod
    def _validate_action(cls, entry_name, name, arg):
        # TODO
        return name, arg

    @classmethod
    def _log_invalid_rule(cls, entry_name, rule_name, rule_arg, message):
        logger.warning(
            'Invalid rule in entry "%s": %s', entry_name, message,
        )
        logger.warning(
            'Offending rule was: "%s": "%s"', rule_name, rule_arg,
        )
