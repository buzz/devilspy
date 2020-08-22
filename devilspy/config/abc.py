"""Abstract base classes for the devilspy configuration."""

from abc import ABCMeta, abstractmethod

from devilspy.logger import main_logger

logger = main_logger.getChild("config")


class AbstractBaseConfigEntity(metaclass=ABCMeta):
    """
    Abstract base class for all configuration elements.

    All subclasses must define a factory method create.
    """

    @classmethod
    def create(cls, data, *args):
        """Validate/transform data, then let subclass parse data."""
        class_ = cls.get_class_from_data(data)  # Entity can use a custom class
        if class_ is None:
            class_ = cls
        validated_data = class_.validate(data)
        instance = class_(*args)
        instance.parse(validated_data)
        return instance

    def parse(self, data):
        """Parse data of this config entity."""

    @classmethod
    def get_class_from_data(cls, _):
        """Get configuration entity class from data."""
        return None

    @classmethod
    @abstractmethod
    def validate(cls, data):
        """Validate/transform data."""


class AbstractBaseConfigEnumerableEntity(AbstractBaseConfigEntity, metaclass=ABCMeta):
    """Abstract base class for configuration elements with index."""

    def __init__(self, idx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idx = idx
