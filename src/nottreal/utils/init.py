
from .log import Logger
from .dir import DirUtils
from argparse import ArgumentTypeError

import importlib, os, pkgutil, sys

class ArgparseUtils:

    def dir_contains_config(dir):
        """
        Does a directory contain the required configuration files and
        are they readable?
        
        If no supplied directory is given (or the default is given), and it
        is invalid, the distribution configuration (in `.cfg-dist`) is used.

        Arguments:
            dir {str} -- Directory relative to this directory

        Raises:
            ArgumentTypeError -- if the user supplies the distribution config
                directory as their choice, or if their supplied choice of 
                directory does not exist, is not readable, or is missing
                the required files

        Returns:
            {str} -- Path to the configuration directory
        """
        if dir == '.cfg-dist':
            raise ArgumentTypeError(('You cannot use the distribution '
                                    'configuration directory'))
        
        dist_dir = '.cfg-dist'
        pwd = DirUtils.pwd() + '/'
        requested_dir = pwd + dir
        
        if not os.path.isdir(requested_dir):
            if dir == 'cfg' and os.path.isdir(pwd + '.cfg-dist'):
                print('%s not found' % requested_dir,
                    '∴ falling back to distribution configuration', sep=' ')
                dir = dist_dir 
                requested_dir = pwd + dist_dir
            else:
                raise ArgumentTypeError((
                        '%s is not a readable directory' % (dir)))
        elif os.access(dir, os.R_OK):
            files = ('settings.cfg', 'categories.tsv', 'messages.tsv')
            for file in files:
                if not os.access(requested_dir + '/' + file, os.R_OK):
                    raise ArgumentTypeError((
                        '%s/%s is not a readable file' % (dir, file)))

        return dir

    def dir_is_writeable(dir):
        """
        Is a directory writeable?

        Arguments:
            dir {str} -- Directory relative to this directory

        Returns:
            {str} -- `dir` if directory is writeable
        
        Raises:
            ArgumentTypeError -- If `dir` is not valid or writeable
        """
        pwd = DirUtils.pwd() + '/'
        
        if dir and not os.path.isdir(pwd + dir):
            raise ArgumentTypeError(
                ('%s is not a valid directory' % dir))
        elif dir and not os.access(dir, os.W_OK):
            raise ArgumentTypeError(
                ('%s is not a writeable directory' % dir))
                
        return dir

class ClassUtils:
    def load_all_subclasses(module_path, subclass, prefix = ''):
        """
        Search a directory/module for files and import classes
        that subclass (can be multi-layer) a class.
        
        Arguments:
            module_path {str} -- Directory to search
            subclass {class} -- Class everthing must inherit from
            prefix {str} -- Prefix from module above (Default: ``)
        """
        for (_, name, ispkg) in pkgutil.iter_modules([module_path]):
            Logger.debug(__name__, 'Loading "%s.py"' % name)
            importlib.import_module('..' + prefix + name, __package__)

        return ClassUtils.get_all_subclasses(subclass)
            
    def get_all_subclasses(rootclass):
        """
        Recursively get all subclasses
        
        Arguments:
            rootclass {class} -- Class to look for subclasses of
        
        Returns:
            [class]
        """
        subclasses = {}
        
        for subclass in rootclass.__subclasses__():
            subclasses[subclass.__name__] = subclass
            subclasses.update(ClassUtils.get_all_subclasses(subclass))

        return subclasses