"""Config parser errors."""


class ConfigValidationError(ValueError):
    """Base error class for all config parser errors."""

    def __init__(self, message, *args, **kwargs):
        """Initialize error with message."""
        super().__init__(*args, **kwargs)
        self.message = message


class InvalidEntryError(ConfigValidationError):
    """Invalid entry encountered."""


class InvalidActionError(ConfigValidationError):
    """Invalid action encountered."""


class InvalidRuleError(ConfigValidationError):
    """Invalid rule encountered."""
