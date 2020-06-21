
import sys
import os
import platform


class DirUtils:

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
