"""devilspy configuration."""

import yaml

from devilspy.config.abc import AbstractBaseConfigEntity
from devilspy.config.entry import Entry
from devilspy.config.errors import ConfigValidationError, InvalidEntryError
from devilspy.logger import main_logger

logger = main_logger.getChild("config")


class Config(AbstractBaseConfigEntity):
    """Configuration class holds and validates rules."""

    def __init__(self, filepath):
        self._filepath = filepath
        self.entries = []

    @classmethod
    def load_yaml_file(cls, filepath):
        """Load configuration from YAML file."""
        try:
            with open(filepath, "r") as configfile:
                data = yaml.safe_load(configfile.read())
                config = cls.create(data, filepath)
                logger.debug("Config: %s", config)
                return config
        except FileNotFoundError:
            logger.warning("Config file not found.")
        except yaml.scanner.ScannerError as error:
            logger.warning("Failed to parse config: %s", error)
        except ConfigValidationError as error:
            logger.warning("Failed to parse config: %s", error.message)
        return None

    def parse(self, data):
        for entry_name, entry_data in data.items():
            try:
                self.entries.append(Entry.create(entry_data, entry_name))
            except InvalidEntryError as error:
                logger.warning("Invalid entry: '%s': %s", entry_name, error.message)

        if not self.entries:
            logger.warning("No entries in config.")

    @classmethod
    def validate(cls, data):
        if not isinstance(data, dict):
            raise InvalidEntryError("Config must be of type dict.")
        return data
