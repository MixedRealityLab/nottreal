
from distutils.dir_util import copy_tree

import os
import platform
import subprocess
import sys


class DirUtils:

    @staticmethod
    def cp(source_dir, target_dir):
        """
        Copy the contents of one directory to another

        Arguments:
            source_dir {str} -- Source directory to copy from
            target_dir {str} -- Target directory to copy top

        Returns:
            {bool}
        """
        return copy_tree(source_dir, target_dir)

    @staticmethod
    def is_empty_or_create(directory):
        if os.path.isdir(directory):
            contents = [f for f in os.listdir(directory)]
            return len(contents) == 0
        else:
            os.mkdir(directory)
            return True

        return False

    @staticmethod
    def pwd():
        """
        Get the present working directory

        Returns:
            {str}
        """
        if getattr(sys, 'frozen', False):
            if platform.system() == 'Darwin':
                return os.path.join(sys._MEIPASS, '..', 'Resources')
            else:
                return sys._MEIPASS
        else:
            return os.getcwd()

    def open_in_os(path):
        """
        Opens in the OS directory explorer/finder

        Arguments:
            path {str} -- Path to open
        """
        if not os.path.isdir(path):
            return False

        if platform.system() == 'Windows':
            explorer = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
            subprocess.run([
                explorer,
                path])
        elif platform.system() == 'Darwin':
            subprocess.call(['open', '-a', 'Finder', path])
        elif platform.system() == 'Linux':
            subprocess.Popen(['xdg-open', path])

    def reveal_file_in_os(path):
        """
        Opens in the OS directory explorer/finder to reveal a file.

        This only works in macOS at the moment.

        Arguments:
            path {str} -- Path to open
        """
        if not os.path.isfile(path):
            return False

        if platform.system() == 'Darwin':
            subprocess.run(['open', '-R', path])
