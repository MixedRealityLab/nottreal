
from ..utils.log import Logger

from PySide2.QtWidgets import (QWidget)

import abc


class AbstractOutputView(QWidget):
    """
    A VUI output window, must be implemented as a {QWidget}

    Extends:
        QWidget
    """
    def __init__(self, nottreal, args):
        """
        A window that displays output

        Don't do anything in this method, the instance is destroyed if
        the output view is not activated

        Arguments:
            nottreal {App} -- Main NottReal class
            args {[str]} -- CLI arguments
        """
        self.nottreal = nottreal
        self.args = args

        super(AbstractOutputView, self).__init__()

    @abc.abstractmethod
    def init_ui(self):
        """
        Initialise the UI

        Decorators:
            abc.abstractmethod

        Returns:
            {bool}
        """
        pass

    @abc.abstractmethod
    def activated(self):
        """
        Return {True} if this output window should receive messages.

        Decorators:
            abc.abstractmethod

        Returns:
            {bool}
        """
        return False

    @abc.abstractmethod
    def get_label(self):
        """
        Return the name of the output view.

        Decorators:
            abc.abstractmethod

        Returns:
            {str}
        """
        pass

    def is_visible(self):
        """
        Is the window visible?

        Returns:
            {bool}
        """
        return self.isVisible()

    def toggle_visibility(self):
        """
        Toggle visibility of the window
        """
        if self.isVisible():
            self.hide()
            self.close()
            Logger.info(__name__, '%s is closed' % self.get_label())
        else:
            self.show()
            Logger.info(__name__, '%s is visible' % self.get_label())

    def toggle_fullscreen(self):
        """
        Toggle fullscreen/windowed mode
        """
        if self.isFullScreen():
            self.showNormal()
            Logger.info(__name__, '%s is windows' % self.get_label())
        else:
            self.showFullScreen()
            Logger.info(__name__, '%s is fullscreen' % self.get_label())

    @abc.abstractmethod
    def set_message(self, text):
        """
        A new message to show immediately

        Arguments:
            text {str} -- Text of the message
        """
        pass

    @abc.abstractmethod
    def set_state(self, state):
        """
        Update the displayed state of the VUI

        Arguments:
            state {models.VUIState} -- New state of the VUI
        """
        pass
