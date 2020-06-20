
from ..utils.log import Logger
from ..models.m_mvc import VUIState
from .c_abstract import AbstractController


class OutputController(AbstractController):
    """
    Create the controller for the output views.

    Extends:
        AbstractController

    """
    def __init__(self, nottreal, args):
        """
        Controller to manage the MVUI window that can be displayed to
        the "user" of the system (i.e. a view that makes this look
        like a real Mobile VUI assistant).

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

    def ready(self):
        for output in self.nottreal.view.output.values():
            output.updated_config(self.nottreal.config)

        if self.args.output_win and self.args.output_win != 'disabled':
            self.toggle_show(self.args.output_win)

    def respond_to(self):
        """
        This class will handle "output" commands

        Returns:
            str -- Label for this controller
        """
        return 'output'

    def toggle_show(self, output):
        """
        Toggle the display of an output window

        Arguments:
            output {str} -- Name of the output to show
        """
        if self.args.dev:
            self.nottreal.view.output[output.lower()].toggle_visibility()
        else:
            try:
                self.nottreal.view.output[output.lower()].toggle_visibility()
            except KeyError:
                Logger.error(__name__, 'No output view "%s"' % output)

    def toggle_maximise(self, output):
        """
        Toggle the fullscreen display the window if it's visible

        Arguments:
            output {str} -- Name of the output to toggle
        """
        try:
            self.nottreal.view.output[output.lower()].toggle_fullscreen()
        except KeyError:
            Logger.error(__name__, 'No output view "%s"' % output)

    def now_speaking(self, text=None, orb=1):
        """
        Show text in the window (if it's visible) while it's been spoken

        Appending is not implemented!

        Keyword Arguments:
            text {str} -- Text to show (default: None}
            orb {int} -- Orb ID, 0 = rest, 1 = speak, 2 = listen,
                         3 = busy (default: 1)
        """
        for output in self.nottreal.view.output.values():
            if output.is_visible():
                output.set_state(orb)
                output.set_message(text)

    def now_resting(self):
        """
        Show that the system is no longer speaking in the MVUI window, nor
        is it doing anything else (if it's visible).
        """
        for output in self.nottreal.view.output.values():
            if output.is_visible():
                output.set_state(VUIState.RESTING)

    def now_listening(self):
        """
        Show that the user is currently being listened to in the MVUI
        window (if it's visible).
        """
        for output in self.nottreal.view.output.values():
            if output.is_visible():
                output.set_state(VUIState.LISTENING)

    def now_computing(self):
        """
        Highlight that a respond is currently being computed in the MUI
        window (if it's visible).
        """
        for output in self.nottreal.view.output.values():
            if output.is_visible():
                output.set_state(VUIState.BUSY)

    def quit(self):
        """
        Close and quit the MVUI window, if it still exists.
        """
        if self._mvui_win:
            self._mvui_win.close()
