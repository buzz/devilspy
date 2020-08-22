"""All possible window actions."""

from abc import ABCMeta, abstractmethod
from gi.repository import Gdk, GdkX11, GLib, Wnck
import Xlib.display

from devilspy.config.abc import AbstractBaseConfigEnumerableEntity
from devilspy.config.errors import InvalidActionError


class AbstractBaseAction(AbstractBaseConfigEnumerableEntity, metaclass=ABCMeta):
    """Abstract base class for all actions."""

    arg_type = None

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
                raise InvalidActionError(cls, "Could not parse.")
        try:
            return ACTION_MAPPING[name]
        except KeyError:
            vals = ACTION_MAPPING.keys()
            raise InvalidActionError(
                cls, "Invalid value for 'name'. Must be one of {}.".format(vals)
            )

    @classmethod
    def validate(cls, data):
        if not isinstance(data, dict):
            raise InvalidActionError(cls, "Action must be of type dict.")

        # Transform action short notation into canonical presentation.
        if len(data.keys()) == 1:
            name = list(data.keys())[0]
            data = {
                "name": name,
                "arg": data[name],
            }

        if "arg" not in data:
            raise InvalidActionError(cls, "Missing key 'arg'.")

        if isinstance(cls.arg_type, tuple):
            is_list = isinstance(data["arg"], list)
            if not is_list:
                raise InvalidActionError(cls, "Field 'arg' must be a list.")
            if len(data["arg"]) != len(cls.arg_type):
                msg = "Field 'arg' must be a list with {} elements.".format(
                    len(cls.arg_type)
                )
                raise InvalidActionError(cls, msg)
            for i, type_ in enumerate(cls.arg_type):
                if type(data["arg"][i]) not in (type_,):
                    msg = "Field 'arg[{}]' must be of type {}.".format(
                        i, type_.__name__
                    )
                    raise InvalidActionError(cls, msg)
        else:
            if type(data["arg"]) not in (cls.arg_type,):
                raise InvalidActionError(
                    cls, "Field 'arg' must be of type {}.".format(cls.arg_type.__name__)
                )

        return data

    @abstractmethod
    def run(self, window, screen):
        """Carry out window action."""

    def __str__(self):
        return "  {}: arg={}".format(type(self).__name__, self.arg)


class ActivateWorkspaceAction(AbstractBaseAction):
    """Switch to another workspace."""

    name = "activate_workspace"
    arg_type = int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_idx = None

    def run(self, window, screen):
        space = screen.get_workspace(self.arg)
        if space:
            active_space = screen.get_active_workspace()
            if active_space and space == active_space:
                return
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
    arg_type = bool

    def run(self, window, screen):
        if self.arg:
            if not window.is_maximized():
                window.maximize()
        else:
            if window.is_maximized():
                window.unmaximize()


class PositionWMAction(AbstractBaseAction):
    """Set window position using window manager."""

    name = "position_wm"
    arg_type = (int, int)

    def run(self, window, screen):
        window.set_geometry(
            Wnck.WindowGravity.CURRENT,
            Wnck.WindowMoveResizeMask.X | Wnck.WindowMoveResizeMask.Y,
            self.arg[0],
            self.arg[1],
            -1,
            -1,
        )


class PositionX11Action(AbstractBaseAction):
    """Set window position using X11."""

    name = "position_x11"
    arg_type = (int, int)

    def run(self, window, screen):
        xid = window.get_xid()
        xdisplay = Xlib.display.Display()
        xwindow = xdisplay.create_resource_object("window", xid)
        xwindow.configure(x=self.arg[0], y=self.arg[1])
        xdisplay.sync()


class SetWindowSizeAction(AbstractBaseAction):
    """Set window size."""

    name = "set_size"
    arg_type = (int, int)


class WorkspaceAction(AbstractBaseAction):
    """Move window to another workspace."""

    name = "workspace"
    arg_type = int

    def run(self, window, screen):
        space = screen.get_workspace(self.arg)
        if space and space != window.get_workspace():
            window.move_to_workspace(space)


ACTION_CLASSES = (
    ActivateWorkspaceAction,
    MaximizeAction,
    PositionWMAction,
    PositionX11Action,
    SetWindowSizeAction,
    WorkspaceAction,
)
ACTION_MAPPING = {cls.name: cls for cls in ACTION_CLASSES}
