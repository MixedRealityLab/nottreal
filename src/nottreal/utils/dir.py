
import sys
import os


class DirUtils:

    @staticmethod
    def pwd():
        """
        Get the present working directory

        Returns:
            {str}
        """
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return os.getcwd()
