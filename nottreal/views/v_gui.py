
from ..utils.init import ClassUtils
from ..utils.log import Logger
from .v_wizard import WizardWindow
from .v_output_abstract import AbstractOutputView

from PySide2.QtCore import (QEvent)
from PySide2.QtGui import (QIcon, QPixmap)
from PySide2.QtWidgets import (QApplication, QStyleFactory)

import sys


class Gui(QApplication):
    """
    The primary GUI application class

    Variables:
        APP_ICON {str} -- Path to the application icon
    """
    APP_ICON = 'nottreal/resources/appicon-512.png'

    def __init__(self, nottreal, args):
        """
        Initialise the GUI application libraries

        Arguments:
            nottreal {App} -- Main NottReal class
            args {[str]} -- CLI arguments
        """
        super().__init__(sys.argv)

        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.nottreal = nottreal
        self.args = args

    def init_ui(self):
        classes = ClassUtils.load_all_subclasses(
            __package__,
            AbstractOutputView)

        self.wizard_window = WizardWindow(
            self.nottreal,
            self.args)

        self.setApplicationDisplayName(self.nottreal.appname)
        self.setWindowIcon(QIcon(QPixmap(self.APP_ICON)))

        self.output = {}
        for name, cls in classes.items():
            if self.args.dev:
                instance = cls(
                    self.nottreal,
                    self.args)

                if instance.activated():
                    self.output[name.lower()] = instance
                    instance.init_ui()
                else:
                    Logger.info(
                        __name__,
                        'Output view "%s" is disabled' % name)
            else:
                try:
                    instance = cls(
                        self.nottreal,
                        self.args)

                    if instance.activated():
                        self.output[name.lower()] = instance
                        instance.init_ui()
                        Logger.info(__name__, 'Loaded output view "%s"' % name)
                    else:
                        Logger.info(
                            __name__,
                            'Output view "%s" is disabled' % name)
                except TypeError:
                    Logger.error(
                        __name__,
                        '"%s" has invalid constructor arguments' % name)

    def run_loop(self):
        """Show the GUI application by starting the UI loop"""
        self.exec_()

    def event(self, e):
        if e.type() == QEvent.FileOpen:
            Logger.debug(
                __name__,
                "Received open file event: "
                + e.file())
            self.nottreal.router(
                'wizard',
                'delayed_set_config',
                directory=e.file())

        return super().event(e)
