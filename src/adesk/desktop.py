# -*- coding: utf-8 -*-

import gtk
import adesk.core as Core

HAS_WNCK = True
try:
    import wnck
except:
    HAS_WNCK = False

# Workaround for new wnck python bindings
if HAS_WNCK:
    try:
        WINDOW_STATE_MINIMIZED = wnck.WINDOW_STATE_MINIMIZED
    except:
        WINDOW_STATE_MINIMIZED = 1<<0

class Wnck:
    def __init__(self, bar):
        self.bar = bar
        self.current_state = False

        # silently ignore x errors
        gtk.gdk.error_trap_push()

        # init screen and hook into WnckSceen's events
        self.screen = wnck.screen_get_default()
        self.screen.force_update()
        self.screen.connect("window_opened", self.window_opened)
        self.screen.connect("window_closed", self.window_closed)
        self.screen.connect("active-workspace-changed", self.workspace_changed)

        windows = self.screen.get_windows()
        for window in windows:
            self.window_opened(self.screen, window)

        self.is_maximized(windows)

    # define event-handlers
    def workspace_changed(self, screen, workspace):
        self.is_maximized()

    def window_opened(self, screen, window):
        window.connect("geometry-changed", self.geometry_changed)
        window.connect("state_changed", self.state_changed)
        if window.is_maximized():
            self.current_state = True
            self.bar.check_window_state()

    def geometry_changed(self, window):
        self.is_maximized()

    def state_changed(self, window, changed, new_state):
        self.is_maximized()

    def window_closed(self, screen, window):
        self.is_maximized()

    def is_maximized(self, windows=None):
        current_wp = self.screen.get_active_workspace()

        if windows == None:
            windows = self.screen.get_windows()

        _state = False

        for window in windows:
            if current_wp == window.get_workspace():
                if window.is_maximized() and not window.is_minimized():
                    _state = True
                    break

        if not self.current_state == _state:
            self.current_state = _state
            self.bar.check_window_state()
