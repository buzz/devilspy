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

        # Expecting arg list
        if isinstance(cls.arg_type, list):
            if not isinstance(data["arg"], list):
                raise InvalidActionError(cls, "Field 'arg' must be a list.")
            if len(data["arg"]) != len(cls.arg_type):
                msg = "Field 'arg' must be a list with {} elements.".format(
                    len(cls.arg_type)
                )
                raise InvalidActionError(cls, msg)

            for i, type_ in enumerate(cls.arg_type):
                cls.validate_arg(type_, data["arg"][i], i)
        else:
            cls.validate_arg(cls.arg_type, data["arg"])

        return data

    @classmethod
    def validate_arg(cls, type_, arg, i=None):
        """Validate action arg field."""
        if not isinstance(type_, tuple):
            type_ = (type_,)
        if type(arg) not in type_:
            idx = "[{}]".format(i) if i else ""
            types = ",".join(t.__name__ for t in type_)
            msg = "Field 'arg{}' must be of type {}.".format(idx, types)
            raise InvalidActionError(cls, msg)

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


class DecorateAction(AbstractBaseAction):
    """(Un)decorate window."""

    name = "decorate"
    arg_type = bool

    def run(self, window, screen):
        xid = window.get_xid()
        gdk_display = GdkX11.X11Display.get_default()
        gdk_window = GdkX11.X11Window.foreign_new_for_display(gdk_display, xid)
        if self.arg:
            gdk_window.set_decorations(Gdk.WMDecoration.ALL)
        else:
            gdk_window.set_decorations(0)


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


class MaximizeHAction(AbstractBaseAction):
    """(Un)maximize window horizontally."""

    name = "maximize_h"
    arg_type = bool

    def run(self, window, screen):
        if self.arg:
            if not window.is_maximized_horizontally():
                window.maximize_horizontally()
        else:
            if window.is_maximized_horizontally():
                window.unmaximize_horizontally()


class MaximizeVAction(AbstractBaseAction):
    """(Un)maximize window vertically."""

    name = "maximize_v"
    arg_type = bool

    def run(self, window, screen):
        if self.arg:
            if not window.is_maximized_vertically():
                window.maximize_vertically()
        else:
            if window.is_maximized_vertically():
                window.unmaximize_vertically()


class MinimizeAction(AbstractBaseAction):
    """(Un)minimize window vertically."""

    name = "minimize"
    arg_type = bool

    def run(self, window, screen):
        if self.arg:
            if not window.is_minimized():
                window.minimize()
        else:
            if window.is_minimized():
                window.unminimize(0)


class OnTopAction(AbstractBaseAction):
    """Set window on top."""

    name = "on_top"
    arg_type = (bool, str)

    def run(self, window, screen):
        if type(self.arg) in (bool,):
            if self.arg:
                window.make_above()
                window.unmake_above()
            else:
                window.unmake_above()
        elif self.arg == "always":
            window.make_above()


class PositionWMAction(AbstractBaseAction):
    """Set window position using window manager."""

    name = "position_wm"
    arg_type = [int, int]

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
    arg_type = [int, int]

    def run(self, window, screen):
        xid = window.get_xid()
        xdisplay = Xlib.display.Display()
        xwindow = xdisplay.create_resource_object("window", xid)
        xwindow.configure(x=self.arg[0], y=self.arg[1])
        xdisplay.sync()


class ShadeAction(AbstractBaseAction):
    """(Un)shade window."""

    name = "shade"
    arg_type = bool

    def run(self, window, screen):
        if self.arg:
            window.shade()
        else:
            window.unshade()


class SizeAction(AbstractBaseAction):
    """Set window size."""

    name = "size"
    arg_type = [int, int]

    def run(self, window, screen):
        window.set_geometry(
            Wnck.WindowGravity.CURRENT,
            Wnck.WindowMoveResizeMask.WIDTH | Wnck.WindowMoveResizeMask.HEIGHT,
            -1,
            -1,
            self.arg[0],
            self.arg[1],
        )


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
    DecorateAction,
    MaximizeAction,
    MaximizeHAction,
    MaximizeVAction,
    MinimizeAction,
    OnTopAction,
    PositionWMAction,
    PositionX11Action,
    ShadeAction,
    SizeAction,
    WorkspaceAction,
)
ACTION_MAPPING = {cls.name: cls for cls in ACTION_CLASSES}
