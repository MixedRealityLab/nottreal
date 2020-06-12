
from .m_abstract import AbstractModel
from ..utils.log import Logger

from collections import OrderedDict

import sys, os, configparser

class ConfigModel(AbstractModel):
    def __init__(self, args):
        """Load data from configuration files.
        
        Arguments:
            args {[arg]} -- Application arguments
        """
        self.config_dir = args.config_dir
        super().__init__(args)

        Logger.debug(__name__, 'Loading data from the configuration file')

        self.config = configparser.ConfigParser()
        self.config.read(args.config_dir + '/settings.cfg')

        Logger.info(__name__, 'Configuration loaded')

    def get(self, section, option):
        return self.config.get(section, option)

    def cfg(self):
        return self.config
