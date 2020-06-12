
from ..utils.log import Logger
from .c_abstract import AbstractController

from datetime import datetime

import os

class DataRecorderController(AbstractController):
    """
    Class to record messages sent to the user
    
    Extends:
        AbstractController
    
    Variables:
        TIMESTAMP_FORMAT {str} -- Timestamp for files and inside the log
        FILE_PREFIX {str} -- Filename prefix
        FILE_EXT {str} -- Filename suffix
    """
    TIMESTAMP_FORMAT = '%Y-%m-%d %H.%M.%S'
    FILE_PREFIX = 'log-'
    FILE_EXT = '.txt'

    def __init__(self, nottreal, args):
        """
        Controller to record messages sent to the users
        
        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        if args.output_dir:
            self._dir = args.output_dir
            timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
            path = '%s%s%s' % (self.FILE_PREFIX, timestamp, self.FILE_EXT)
            self._filepath = os.path.join(self._dir, path)

            try:
                self._file = open(self._filepath, mode='a')
                if self._file:
                    self._enable = True
                    Logger.info(
                        __name__,
                        'Messages will be recorded to "%s"' % self._filepath)
            except IOError:
                self._enable = False
                Logger.critical(
                    __name__,
                    'Failed to open "%s" to record messages' % self._filepath)
        else:
            self._enable = False
            Logger.info(
                __name__,
                'Disable recording of messages to the data log')

    def quit(self):
        """
        Close and quit the data recorder if it still exists
        """
        if self._enable and self._file:
            self._file.close()

    def respond_to(self):
        """
        This class will handle 'data' commands only.
        
        Returns:
            str -- Label for this controller
        """
        return 'data'

    def custom_event(self, id, text):
        """
        Record a custom event to the log
        
        Arguments:
            text {str} -- Text spoken
        """
        if self._enable:
            Logger.debug(
                __name__,
                'Log event for "%s" with message "%s"' % (id, text))

            timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
            print(
                '%s\t_Event\t%s\t\t%s' % (timestamp, id, text),
                file=self._file,
                flush=True)

    def raw_text(self, text):
        """
        Record some text being spoken to the data log
        
        Arguments:
            text {str} -- Text spoken
        """
        if self._enable:
            timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
            print(
                '%s\t\t\t\t%s' % (timestamp, text),
                file=self._file,
                flush=True)

    def prepared_text(self, text, cat, id, slots):
        """
        Record some text being spoken to the data log that was from a
        prepared message
        
        Arguments:
            text {str} -- Text spoken
            cat {int} -- Category ID of the prepared message
            id {int} -- ID of the prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        if self._enable:
            timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
            print(
                '%s\t%s\t%s\t%s\t%s' % (timestamp, cat, id, slots, text),
                file=self._file,
                flush=True)
        