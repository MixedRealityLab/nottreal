
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

        self.config = configparser.ConfigParser()
        self.config.read(args.config_dir + '/settings.cfg')

        Logger.info(__name__, 'Loaded configuration')

    def get(self, section, option):
        return self.config.get(section, option)

    def cfg(self):
        return self.config
