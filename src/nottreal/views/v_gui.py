
from ..utils.init import ClassUtils
from ..utils.log import Logger
from .v_wizard import WizardWindow
from .v_output_abstract import AbstractOutputView

from PySide2.QtGui import (QIcon, QPixmap)
from PySide2.QtWidgets import (QApplication, QStyleFactory)

import sys


class Gui:
    """
    The primary GUI application class

    Variables:
        APP_ICON {str} -- Path to the application icon
    """
    APP_ICON = 'src/nottreal/resources/appicon-512.png'

    def __init__(self, nottreal, args):
        """
        Initialise the GUI application libraries

        Arguments:
            nottreal {App} -- Main NottReal class
            args {[str]} -- CLI arguments
        """
        self._qtapp = QApplication(sys.argv)
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

        self._qtapp.setApplicationDisplayName(self.nottreal.appname)
        self._qtapp.setWindowIcon(QIcon(QPixmap(self.APP_ICON)))

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
        self._qtapp.exec_()

    def quit(self):
        """Quit the GUI application"""
        self._qtapp.quit()
