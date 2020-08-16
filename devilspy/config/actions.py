"""All possible window actions."""

from abc import ABCMeta, abstractmethod
from gi.repository import GLib

from devilspy.config.abc import AbstractBaseConfigEnumerableEntity
from devilspy.config.errors import InvalidActionError


class AbstractBaseAction(AbstractBaseConfigEnumerableEntity, metaclass=ABCMeta):
    """Abstract base class for all actions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg = None

    def parse(self, data):
        self.arg = data["arg"]

    @classmethod
    def get_class_from_data(cls, data):
        try:
            name = data["name"]
        except (KeyError, TypeError):
            try:
                name = list(data.keys())[0]  # Short notation?
            except (AttributeError, IndexError):
                raise InvalidActionError("Could not parse.")
        try:
            return ACTION_MAPPING[name]
        except KeyError:
            vals = ACTION_MAPPING.keys()
            raise InvalidActionError(
                "Invalid value for 'name'. Must be one of {}.".format(vals)
            )

    @classmethod
    def validate(cls, data):
        if not isinstance(data, dict):
            raise InvalidActionError("Action must be of type dict.")

        # Transform action short notation into canonical presentation.
        if len(data.keys()) == 1:
            name = list(data.keys())[0]
            return {
                "name": name,
                "arg": data[name],
            }

        if "arg" not in data:
            raise InvalidActionError("Missing key 'arg'.")

        return data

    @abstractmethod
    def run(self, window, screen):
        """Carry out window action."""


class ActivateWorkspaceAction(AbstractBaseAction):
    """Switch to another workspace."""

    name = "activate_workspace"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_idx = None

    @classmethod
    def validate(cls, data):
        data = super().validate(data)
        # TODO: support True to switch to window workspace?
        if not isinstance(data["arg"], int):
            raise InvalidActionError("Field 'arg' must be of type int.")
        return data

    def run(self, window, screen):
        space = screen.get_workspace(self.arg)
        if space and space != screen.get_active_workspace():
            # Delay workspace switch or some window managers have display issues
            GLib.timeout_add(100, self._delayed_activate_workspace, space)

    @staticmethod
    def _delayed_activate_workspace(space):
        """Delayed workspace switch."""
        space.activate(0)
        return False  # Notify GLib to cancel this timeout


class MaximizeAction(AbstractBaseAction):
    """(Un)maximize window."""

    name = "maximize"

    @classmethod
    def validate(cls, data):
        data = super().validate(data)
        if not isinstance(data["arg"], bool):
            raise InvalidActionError("Field 'arg' must be of type bool.")
        return data

    def run(self, window, screen):
        if self.arg:
            if not window.is_maximized():
                window.maximize()
        else:
            if window.is_maximized():
                window.unmaximize()


class WorkspaceAction(AbstractBaseAction):
    """Move window to another workspace."""

    name = "workspace"

    @classmethod
    def validate(cls, data):
        data = super().validate(data)
        if not isinstance(data["arg"], int):
            raise InvalidActionError("Field 'arg' must be of type int.")
        return data

    def run(self, window, screen):
        space = screen.get_workspace(self.arg)
        if space and space != window.get_workspace():
            window.move_to_workspace(space)


ACTION_CLASSES = (ActivateWorkspaceAction, MaximizeAction, WorkspaceAction)
ACTION_MAPPING = {cls.name: cls for cls in ACTION_CLASSES}
