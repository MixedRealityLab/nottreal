
from ..utils.dir import DirUtils
from ..utils.log import Logger

import configparser
import os


class ConfigModel:
    def __init__(self, args):
        """
        Load data from configuration files

        Arguments:
            args {[arg]} -- Application arguments
        """
        self.config_dir = args.config_dir
        if self.config_dir == 'cfg':
            self.config_dir = DirUtils.pwd() + '/' + self.config_dir

        self._listeners = []
        self.config = configparser.ConfigParser()

    def update(self, directory):
        filepath = directory + '/settings.cfg'
        if os.path.isfile(filepath):
            self.config.read(filepath)
            Logger.info(
                __name__,
                'Loaded configuration file from "%s"' % filepath)

            for listener in iter(self._listeners):
                listener(self)
        else:
            raise FileNotFoundError('No such file "%s"' % filepath)

    def add_listener(self, method):
        self._listeners.append(method)

    def get(self, section, option):
        return self.config.get(section, option)

    def cfg(self):
        return self.config
