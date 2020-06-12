
from ..utils.init import ClassUtils
from ..utils.dir import *
from ..utils.log import Logger
from .v_wizard import WizardWindow
from .v_output_abstract import AbstractOutputView

from PySide2.QtWidgets import (QApplication, QStyleFactory)

import importlib
import pkgutil
import sys


class Gui:
    """The primary GUI application class"""
    def __init__(self, nottreal, args, data, config):
        """
        Initialise the GUI application libraries

        Arguments:
            nottreal {App} -- Main NottReal class
            args {[str]} -- CLI arguments
            data {TSVModel} -- Data from static data files
            config {ConfigModel} -- Data from configuration files
        """
        self._qtapp = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.nottreal = nottreal
        self.args = args
        self.data = data
        self.config = config

    def init_ui(self):
        module_path = DirUtils.pwd() + '/src/nottreal/views'
        classes = ClassUtils.load_all_subclasses(
            module_path,
            AbstractOutputView,
            'views.')

        self.wizard_window = WizardWindow(
            self.nottreal,
            self.args,
            self.data,
            self.config)

        self.output = {}
        for name, cls in classes.items():
            if self.args.dev:
                instance = cls(
                    self.nottreal,
                    self.args,
                    self.data,
                    self.config)

                if instance.activated():
                    self.output[name.lower()] = instance
                    instance.init_ui()
                    Logger.info(__name__, 'Loaded output view "%s"' % name)
                else:
                    Logger.info(
                        __name__,
                        'Output view "%s" is disabled' % name)
            else:
                try:
                    instance = cls(
                        self.nottreal,
                        self.args,
                        self.data,
                        self.config)

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
