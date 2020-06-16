
from ..utils.log import Logger
from ..models.m_mvc import WizardOption
from .c_abstract import AbstractController

from datetime import datetime

import os


class DataRecorderController(AbstractController):
    """
    Class to record messages sent to the user

    Extends:
        AbstractController

    Variables:
        DEFAULT_DIRECTORY {str} -- Default directory
        TIMESTAMP_FORMAT {str} -- Timestamp for files and inside the log
        FILE_PREFIX {str} -- Filename prefix
        FILE_EXT {str} -- Filename suffix
    """
    DEFAULT_DIRECTORY = 'data'
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

        self._dir = args.output_dir
        if self._dir is None:
            self._dir = self.DEFAULT_DIRECTORY

        self._enablable = False
        self._enabled = False

    def ready_order(self, responder=None):
        """
        We should be readied late

        Arguments:
            responder {str} -- Will only work for the {voice_root}
                               responder
        """
        return 50

    def ready(self, responder=None):
        """
        Setup and select the default data directory if it exists

        Arguments:
            responder {str} -- Ignored
        """
        Logger.debug(__name__, 'Setting up data logging')
        self._set_directory(self._dir)

        self.nottreal.router(
            'wizard',
            'register_option',
            label='Enable data recording',
            method=self.enable_data_output,
            opt_cat=WizardOption.CAT_WIZARD,
            opt_type=WizardOption.BOOLEAN,
            default=self._enabled,
            order=0,
            group='data')

        self.nottreal.router(
            'wizard',
            'register_option',
            label='Select data directory',
            method=self._set_directory,
            opt_cat=WizardOption.CAT_WIZARD,
            opt_type=WizardOption.DIRECTORY,
            default=self._dir,
            order=1,
            group='data')

    def enable_data_output(self, state):
        """
        Enable/disable data recording (if possible)

        Arguments:
            state {bool} -- New requested state
        """
        if self._enablable:
            if state:
                Logger.info(__name__, 'Enabled recording of data')
                self._enabled = True
                    
                self.router(
                    'wizard',
                    'data_recording_enabled',
                    state=True)
            else:
                Logger.info(__name__, 'Disabled recording of data')
                self._enabled = False
                    
                self.router(
                    'wizard',
                    'data_recording_enabled',
                    state=False)

            return True
        else:
            Logger.error(
                __name__,
                'Could not enable data recording, see earlier error message')
            return False

    def _set_directory(self, new_dir):
        self._dir = new_dir
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        path = '%s%s%s' % (self.FILE_PREFIX, timestamp, self.FILE_EXT)
        self._filepath = os.path.join(self._dir, path)

        try:
            self._file = open(self._filepath, mode='a')
            if self._file:
                Logger.info(
                    __name__,
                    'Set data directory to "%s"' % self._filepath)
                    
                self._enablable = True
                self.enable_data_output(True)
        except IOError:
            Logger.warning(
                __name__,
                'Failed to open "%s" to record data' % self._filepath)

            self._enablable = False
            self.enable_data_output(False)

    def quit(self):
        """
        Close and quit the data recorder if it still exists
        """
        if self._enabled and self._file:
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
        if not self._enabled:
            return

        Logger.debug(
            __name__,
            'Log event for "%s" with message "%s"' % (id, text))

        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        print(
            '%s\t_Event\t%s\t\t%s' % (timestamp, id, text),
            file=self._file,
            flush=True)

    def transcribed_text(self, text):
        """
        Record some text that was transcribed to the data log

        Arguments:
            text {str} -- Text spoken
        """
        if not self._enabled:
            return

        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        print(
            '%s\t_Transcribed\t\t\t\t%s' % (timestamp, text),
            file=self._file,
            flush=True)

    def sent_raw_message(self, text):
        """
        Record some text being spoken to the data log

        Arguments:
            text {str} -- Text spoken
        """
        if not self._enabled:
            return

        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        print(
            '%s\t\t\t\t%s' % (timestamp, text),
            file=self._file,
            flush=True)

    def sent_prepared_message(self, text, cat, id, slots):
        """
        Record some text being spoken to the data log that was from a
        prepared message

        Arguments:
            text {str} -- Text spoken
            cat {int} -- Category ID of the prepared message
            id {int} -- ID of the prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        if not self._enabled:
            return

        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        print(
            '%s\t%s\t%s\t%s\t%s' % (timestamp, cat, id, slots, text),
            file=self._file,
            flush=True)
