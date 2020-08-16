"""devilspy configuration."""

import yaml

from devilspy.constants import (
    ACTION_ARG_VALIDATORS,
    ALLOWED_ACTIONS,
    FIELD_NAMES,
    RULE_NAMES,
)
from devilspy.logger import main_logger

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
        # Expect config to be dict
        try:
            items = config.items()
        except AttributeError:
            logger.warning("Config must have a single dict of entries.")
            return False

        # Validate entries
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
        for key, validate in (
            ("actions", cls._validate_action),
            ("rules", cls._validate_rule),
        ):
            # Check key presence and type
            try:
                items = entry[key]
            except KeyError:
                logger.warning("Missing key '%s' in entry '%s'!", key, entry_name)
                return None
            if not isinstance(items, list):
                logger.warning("'{}' must be list in entry '%s'!", key, entry_name)
                return None

            # Validate items
            validated_items = [
                validate(entry_name, i, item) for i, item in enumerate(items)
            ]
            entry[key] = list(filter(None, validated_items))

        return entry

    @classmethod
    def _validate_rule(cls, entry_name, i, rule):
        # Exact string matcher shortcut notation
        if len(rule.keys()) == 1:
            field = list(rule.keys())[0]
            rule = {
                "match": "exact",
                "field": field,
                "val": rule[field],
            }

        # String matcher rule
        if "match" in rule:
            return cls._validate_string_matcher(entry_name, i, rule)

        cls._log_invalid_rule("Could not parse rule.", i, rule, entry_name)
        return None

    @classmethod
    def _validate_string_matcher(cls, entry_name, i, rule):
        # Check key presence
        for k in ("field", "val"):
            if k not in rule:
                cls._log_invalid_rule(
                    "Missing '{}' key.".format(k), i, rule, entry_name
                )
                return None

        # Check key values
        for k, allowed in (
            ("match", RULE_NAMES),
            ("field", FIELD_NAMES),
        ):
            if rule[k] not in allowed:
                msg = "Value of '{}' must be one of {}.".format(k, allowed)
                cls._log_invalid_rule(msg, i, rule, entry_name)
                return None

        # Check val
        if isinstance(rule["val"], str):
            rule["val"] = [rule["val"]]  # Make sure val is a list
        elif not (
            isinstance(rule["val"], list)
            and all(isinstance(item, str) for item in rule["val"])
        ):
            type_name = type(rule["val"]).__name__
            msg = "'val' must be string or list of strings (got {})."
            cls._log_invalid_rule(msg.format(type_name), i, rule, entry_name)
            return None

        return rule

    @classmethod
    def _validate_action(cls, entry_name, i, action):
        # Action shortcut notation
        if len(action.keys()) == 1:
            name = list(action.keys())[0]
            action = {
                "name": name,
                "arg": action[name],
            }

        # Check key presence
        for k in ("name", "arg"):
            if k not in action:
                cls._log_invalid_action(
                    "Missing '{}' key.".format(k), i, action, entry_name
                )
                return None

        # Check allowed actions
        if action["name"] not in ALLOWED_ACTIONS:
            msg = "Value of 'name' must be one of {}.".format(ALLOWED_ACTIONS)
            cls._log_invalid_action(msg, i, action, entry_name)
            return None

        # Check arg type
        result = ACTION_ARG_VALIDATORS[action["name"]](action["arg"])
        if result is not None:
            msg = "Could not validate value of 'arg': {}".format(result)
            cls._log_invalid_action(msg, i, action, entry_name)
            return None

        return action

    @classmethod
    def _log_invalid_action(cls, message, i, action, entry_name):
        cls._log_invalid_item("action", message, i, action, entry_name)

    @classmethod
    def _log_invalid_rule(cls, message, i, rule, entry_name):
        cls._log_invalid_item("rule", message, i, rule, entry_name)

    @classmethod
    def _log_invalid_item(cls, item_type, message, i, item, entry_name):
        logger.warning(
            "Invalid %s #%d in entry '%s': %s", item_type, i, entry_name, message
        )
        logger.warning("Offending %s: %s", item_type, item)
