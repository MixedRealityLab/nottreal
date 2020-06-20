
from .log import Logger
from .dir import DirUtils

from argparse import ArgumentTypeError

import importlib
import os
import pkgutil


class ArgparseUtils:

    @staticmethod
    def dir_contains_config(dir):
        """
        Does a directory contain the required configuration files and
        are they readable?

        If no supplied directory is given (or the default is given), and it
        is invalid, the distribution configuration (in `dist.cfg`) is used.

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
        if dir == 'dist.cfg':
            raise ArgumentTypeError(('You cannot use the distribution '
                                    'configuration directory'))

        dist_dir = 'dist.cfg'
        pwd = DirUtils.pwd() + '/'
        requested_dir = pwd + dir

        if not os.path.isdir(requested_dir):
            if dir == 'cfg' and os.path.isdir(pwd + 'dist.cfg'):
                print(
                    '%s not found' % requested_dir,
                    '∴ falling back to distribution configuration',
                    sep=' ')
                dir = dist_dir
                requested_dir = pwd + dist_dir
            else:
                raise ArgumentTypeError((
                        '%s is not a readable directory' % (requested_dir)))
        elif os.access(dir, os.R_OK):
            files = ('settings.cfg', 'categories.tsv', 'messages.tsv')
            for file in files:
                if not os.access(requested_dir + '/' + file, os.R_OK):
                    raise ArgumentTypeError((
                        '%s/%s is not a readable file'
                        % (requested_dir, file)))

        return dir

    @staticmethod
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
    @staticmethod
    def load_all_subclasses(package, subclass):
        """
        Search a directory/package for files and import classes
        that subclass (can be multi-layer) a class.

        Arguments:
            package {str or module} -- Package to search
            subclass {class} -- Class everthing must inherit from
        """
        if type(package) == str:
            package = importlib.import_module(package)

        path = package.__path__
        prefix = package.__name__ + "."

        for importer, name, ispkg in pkgutil.walk_packages(path):
            if not ispkg:
                Logger.debug(__name__, 'Loading "%s.py"' % name)
                importlib.import_module(prefix + name)

        return ClassUtils.get_all_subclasses(subclass)

    @staticmethod
    def get_all_subclasses(rootclass):
        """
        Recursively get all subclasses

        Arguments:
            rootclass {class} -- Class to look for subclasses of

        Returns:
            {[class]}
        """
        subclasses = {}

        for subclass in rootclass.__subclasses__():
            subclasses[subclass.__name__] = subclass
            subclasses.update(ClassUtils.get_all_subclasses(subclass))

        return subclasses

    @staticmethod
    def is_subclass(test, rootclass):
        """
        Recursively get all subclasses

        Arguments:
            test {class/str}  -- Class to test
            rootclass {class} -- Class to see if the proposed class is
                                 a subclass of

        Returns:
            {bool}
        """
        try:
            ClassUtils._cached_subclasses[rootclass.__name__]
        except Exception:
            ClassUtils._cached_subclasses = {}
            ClassUtils._cached_subclasses[rootclass.__name__] = \
                ClassUtils.get_all_subclasses(rootclass)
        finally:
            subclasses = ClassUtils._cached_subclasses[rootclass.__name__]

        if isinstance(test, type):
            test = test.__name__

        for subclass in iter(subclasses):
            if subclass == test:
                return True

        return False
