
from ..utils.log import Logger
from ..models.m_mvc import WizardAlert, WizardOption
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

        self._enablable = False
        self._init_enabled = False
        self._file = None
        self._completed_initiation = False

    def ready_order(self, responder=None):
        """
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

        self._opt_enabled = WizardOption(
                key=__name__ + '.enable',
                label='Enable data recording',
                method=self.enable_data_output,
                category=WizardOption.CAT_CORE,
                choose=WizardOption.CHOOSE_BOOLEAN,
                default=self._init_enabled,
                order=0,
                group='data',
                restorable=True)
        self.nottreal.router(
            'wizard',
            'register_option',
            option=self._opt_enabled)

        if self.args.output_dir is None:
            directory = self.DEFAULT_DIRECTORY
            restore = True
        else:
            directory = self.args.output_dir
            restore = False

        self._opt_dir = WizardOption(
                key=__name__ + '.dir',
                label='Select data directory…',
                method=self._set_directory,
                category=WizardOption.CAT_CORE,
                choose=WizardOption.CHOOSE_DIRECTORY,
                default=directory,
                order=1,
                group='data',
                restorable=True,
                restore=restore)
        self.nottreal.router(
            'wizard',
            'register_option',
            option=self._opt_dir)

        self._set_directory(self._opt_dir.value)

        self._completed_initiation = True

    def quit(self):
        """
        Close and quit the data recorder if it still exists
        """
        if self._enabled and self._file is not None:
            self._file.close()

    def respond_to(self):
        """
        This class will handle 'data' commands only.

        Returns:
            str -- Label for this controller
        """
        return 'data'

    def enable_data_output(self, value):
        """
        Enable/disable data recording (if possible)

        Arguments:
            value {bool} -- New requested state

        Return:
            {bool} -- {True} if data recording state waas changed
        """
        if self._enablable:
            Logger.info(
                __name__,
                'Set data recording to %r' % value)

            self.router(
                'wizard',
                'data_recording_enabled',
                state=value)

            return True
        else:
            Logger.error(
                __name__,
                'Could not enable data recording')

            if self._completed_initiation:
                alert = WizardAlert(
                    'Error',
                    'Cannot enable data recording as the data directory'
                    + ' is not valid.\n\nPlease set a data directory.',
                    WizardAlert.LEVEL_ERROR)

                self.router('wizard', 'show_alert', alert=alert)

            return False

    def _set_directory(self, new_dir, override=None):
        """
        Set the data recording directory and enable data
        recording

        Arguments:
            new_dir {str} -- Path to new directory

        Keyword arguments:
            override {bool} -- Enable/disable data output

        Return:
            {bool} -- {True} if the data recording directory was
                      changed
        """
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        path = '%s%s%s' % (self.FILE_PREFIX, timestamp, self.FILE_EXT)
        filepath = os.path.join(new_dir, path)

        try:
            file_object = open(filepath, mode='a')
            if file_object:
                self._file = file_object
                Logger.info(
                    __name__,
                    'Set data file to "%s"' % filepath)

                self._enablable = True
                self._init_enabled = True
                self._opt_enabled.change(True
                                         if override is None
                                         else override)
        except IOError:
            Logger.warning(
                __name__,
                'Failed to open "%s" to record data' % filepath)

            self._enablable = False
            self._opt_enabled.change(False)
            return False

        if self._opt_enabled.ui is not None:
            try:
                self.nottreal.router(
                    'wizard',
                    'update_option',
                    option=self._opt_enabled)
            except AttributeError:
                pass
            finally:
                return True

    def custom_event(self, id, text):
        """
        Record a custom event to the log

        Arguments:
            text {str} -- Text spoken
        """
        if not self._opt_enabled.value:
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
        if not self._opt_enabled.value:
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
        if not self._opt_enabled.value:
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
        if not self._opt_enabled.value:
            return

        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        print(
            '%s\t%s\t%s\t%s\t%s' % (timestamp, cat, id, slots, text),
            file=self._file,
            flush=True)
