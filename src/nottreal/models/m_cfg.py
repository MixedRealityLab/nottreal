
from ..utils.log import Logger

import configparser


class ConfigModel:
    def __init__(self, args):
        """
        Load data from configuration files

        Arguments:
            args {[arg]} -- Application arguments
        """
        self.config_dir = args.config_dir

        Logger.debug(__name__, 'Loading data from the configuration file')

        self._listeners = []
        self.config = configparser.ConfigParser()

    def update(self, directory):
        self.config.read(directory + '/settings.cfg')
        Logger.info(__name__, 'Loaded configuration file')

        for listener in iter(self._listeners):
            listener(self)

    def add_listener(self, method):
        self._listeners.append(method)

    def get(self, section, option):
        return self.config.get(section, option)

    def cfg(self):
        return self.config
