
from .log import Logger
from .dir import DirUtils

from argparse import ArgumentTypeError

import importlib
import os
import platform
import pkgutil


class ArgparseUtils:
    
    def init_darwin():
        """
        Initiate and register for Apple Event manager
        From https://github.com/mattneub/appscript/blob/master/
                py-aemreceive/trunk/lib/aemreceive/main.py
        """
#        if platform.system() == 'Darwin':
#            Logger.info(__name__, 'Hello, Darwin')

#            Logger.debug(__name__, 'Loading "darwin" module')
#            darwin = importlib.import_module('nottreal.utils.darwin')
#            ArgparseUtils = darwin.DarwinUtils()

    @staticmethod
    def dir_contains_config(dir):
        """
        Does a directory contain the required configuration files and
        are they readable?

        If no supplied directory is given (or the default is given), and it
        is invalid, the distribution configuration (in `dist.nrc`) is used.

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
        if dir == 'dist.nrc':
            raise ArgumentTypeError(('You cannot use the distribution '
                                    'configuration directory'))

        dist_dir = 'dist.nrc'
        pwd = DirUtils.pwd() + os.path.sep

        if dir[0] != os.path.sep:
            requested_dir = pwd + dir
        else:
            requested_dir = dir

        if not os.path.isdir(requested_dir):
            if dir == 'cfg.nrc' and os.path.isdir(pwd + 'dist.nrc'):
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
                if not os.access(requested_dir + os.path.sep + file, os.R_OK):
                    raise ArgumentTypeError((
                        '%s%s%s is not a readable file'
                        % (requested_dir, os.path.sep, file)))

        return requested_dir

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
        pwd = DirUtils.pwd() + os.path.sep

        if dir and not os.path.isdir(pwd + dir):
            raise ArgumentTypeError(
                ('%s is not a valid directory' % dir))
        elif dir and not os.access(dir, os.W_OK):
            raise ArgumentTypeError(
                ('%s is not a writeable directory' % dir))

        return pwd + dir


class ClassUtils:
    @staticmethod
    def list_all_modules(package):
        """
        List all modules in a package

        Arguments:
            package {str} -- Package to search
        """

        return [name
                for _, name, _
                in pkgutil.iter_modules([package.replace('.', os.path.sep)])]

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
        prefix = package.__name__ + '.'
        modules = [m[1] for m in pkgutil.iter_modules(path, prefix)]

        # pyinstaller workaround from
        # https://github.com/pyinstaller/pyinstaller/issues/1905
        #   #issuecomment-525221546
        toc = set()
        for importer \
                in pkgutil.iter_importers(package.__name__.partition('.')[0]):
            if hasattr(importer, 'toc'):
                toc |= importer.toc
        for name in toc:
            if name.startswith(prefix):
                modules.append(name)

        for name in modules:
            Logger.debug(__name__, 'Loading "%s.py"' % name)
            try:
                importlib.import_module(name)
            except ImportError as e:
                Logger.critical(
                    __name__,
                    'Could not import "%s": %s' % (name, e))

        return ClassUtils.get_all_subclasses(subclass)

    @staticmethod
    def _load_all_subclasses_pyinstaller():
        toc = set()
        importers = pkgutil.iter_importers(__package__)
        for i in importers:
            if hasattr(i, 'toc'):
                toc |= i.toc
        return toc

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
