
from ..utils.log import Logger
from ..models.m_mvc import WizardOption
from .c_abstract import AbstractController

import os
import json


class AppStateController(AbstractController):
    """
    Class to load/save the application state

    Extends:
        AbstractController

    Variables:
        DEFAULT_DIRECTORY {str} -- Default directory
        FILENAME {str} -- Filename
        ITERATIVE_SAVING {bool} -- Save continuously or on close?
    """
    DEFAULT_DIRECTORY = 'cfg'
    FILENAME = 'appstate.json'
    ITERATIVE_SAVING = True

    def __init__(self, nottreal, args):
        """
        Controller to record messages sent to the users

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self._dir = args.config_dir
        if self._dir is None:
            self._dir = self.DEFAULT_DIRECTORY

        self._force_off = args.nostate
        self._opt_enabled = None
        self._enablable = False
        self._state_data = {}

        WizardOption.set_app_state_responder(self)

    def ready_order(self, responder=None):
        """
        Arguments:
            responder {str} -- Will only work for the {voice_root}
                               responder
        """
        return 0

    def ready(self, responder=None):
        """
        Setup and select the default config directory if it exists

        Arguments:
            responder {str} -- Ignored
        """
        if self._force_off:
            Logger.debug(__name__, 'App state saving disabled')
            return

        Logger.debug(__name__, 'Setting up app state saving')

        self._opt_enabled = WizardOption(
                label='Save application state',
                method=self.enable_app_state_output,
                opt_cat=WizardOption.CAT_CORE,
                opt_type=WizardOption.BOOLEAN,
                default=True,
                order=0,
                group='appstate',
                restorable=False)

        self.nottreal.router(
            'wizard',
            'register_option',
            option=self._opt_enabled)

    def quit(self):
        """
        Close and quit the data recorder if it still exists
        """
        if self._force_off:
            return

        if self._opt_enabled.value and not self.ITERATIVE_SAVING:
            self._write_state()

    def respond_to(self):
        """
        This class will handle 'appstate' commands only.

        Returns:
            str -- Label for this controller
        """
        return 'appstate'

    def enable_app_state_output(self, state):
        """
        Enable/disable app state (if possible)

        Arguments:
            state {bool} -- New requested state
        """
        if self._enablable and not self._force_off:
            if state:
                Logger.info(__name__, 'Enabled app state saving')
            else:
                Logger.info(__name__, 'Disabled app state saving')

            try:
                self._opt_enabled.change(state)
            except AttributeError:
                pass

            return True
        else:
            Logger.error(
                __name__,
                'Could not enable app state saving, see earlier error message')
            return False

    def set_directory(self, directory, is_initial_load=False):
        """
        Set the config recording directory and enable app state
        recording

        Arguments:
            directory {str} -- Path to new directory
            is_initial_load {bool} - Override auto re-enable
        """
        if self._force_off:
            return

        self._dir = directory
        self._filepath = os.path.join(self._dir, self.FILENAME)
        
        contents_corrupt = False

        try:
            if os.path.exists(self._filepath):
                with open(self._filepath, 'rt') as state_file:
                    self._state_data = json.load(state_file)
        except json.decoder.JSONDecodeError as e:
            Logger.critical(
                __name__,
                'App state file is invalid, will be overwritten!')

            if not len(self._state_data):
                self._state_data = {'options': {}}
                
            contents_corrupt = True

        try:
            statefile = open(self._filepath, mode='w')
            if statefile:
                Logger.info(
                    __name__,
                    'Set app state file to "%s"' % self._filepath)

                self._enablable = True
                self.enable_app_state_output(True)
            statefile.close()

            if contents_corrupt:
                self._write_state()
        except IOError:
            Logger.warning(
                __name__,
                'Failed to open "%s" to save app state' % self._filepath)

            self._enablable = False
            self.enable_app_state_output(False)

        try:
            if self._opt_enabled.ui is not None:
                self.nottreal.router(
                    'wizard',
                    'update_option',
                    option=self._opt_enabled)
        except AttributeError:
            pass

    def _write_state(self):
        """
        Write the state to the file
        """
        if self._force_off or not self._opt_enabled.value:
            return

        Logger.debug(__name__, 'Saving application state')
        with open(self._filepath, mode='w') as statefile:
            json.dump(self._state_data, statefile)

    def get_option(self, opt_cat, label, default):
        """
        Get an option from the state or the default value

        Arguments:
            opt_cat {str} -- Option category
            label {WizardOption} -- Option label to fetch
            default {mixed} -- Default value if option doesn't exist
        """
        if self._force_off or not self._opt_enabled:
            return default

        cat = str(opt_cat)

        try:
            value = self._state_data['options'][cat][label]
        except Exception:
            value = default
        finally:
            return value

    def save_option(self, option):
        """
        Save an option to the state

        Arguments:
            option {WizardOption} -- Option to save
        """
        if self._force_off or not self._opt_enabled:
            return

        cat = str(option.opt_cat)

        try:
            if cat not in self._state_data['options']:
                self._state_data['options'][cat] = {}
        except KeyError:
            self._state_data['options'] = {}
            if cat not in self._state_data['options']:
                self._state_data['options'][cat] = {}

        self._state_data['options'][cat][option.label] = \
            option.value

        if self.ITERATIVE_SAVING:
            self._write_state()
