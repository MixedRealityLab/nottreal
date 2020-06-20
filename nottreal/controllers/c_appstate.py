
from ..utils.dir import DirUtils
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
        ALWAYS_SAVE_ON_QUIT {bool} -- Always save on quit too
    """
    DEFAULT_DIRECTORY = 'cfg'
    FILENAME = 'appstate.json'
    ITERATIVE_SAVING = True
    ALWAYS_SAVE_ON_QUIT = True

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
        self._options = {}

        self._init_state = True

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
                key=__name__ + '.save',
                label='Save application state',
                method=self.enable_app_state_output,
                category=WizardOption.CAT_CORE,
                choose=WizardOption.CHOOSE_BOOLEAN,
                default=self._init_state,
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

        if self._opt_enabled.value \
                and (not self.ITERATIVE_SAVING or self.ALWAYS_SAVE_ON_QUIT):
            self._write_state()

    def respond_to(self):
        """
        This class will handle 'appstate' commands only.

        Returns:
            str -- Label for this controller
        """
        return 'appstate'

    def enable_app_state_output(self, value):
        """
        Enable/disable app state (if possible)

        Arguments:
            state {bool} -- New requested state

        Return:
            {bool} -- {True} if app state saving state was changed
        """
        if ((self._enablable and value) or not value) and not self._force_off:
            Logger.info(__name__, 'Set app state saving to %r' % value)
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

        if not is_initial_load:
            self._write_state()

        dir_name = directory.replace(DirUtils.pwd() + os.path.sep, '')
        if dir_name == 'dist.cfg':
            Logger.critical(
                __name__,
                'Cannot save app state to distribution configuration')
            self._enablable = False
            self._init_state = False
            try:
                self._opt_enabled.change(False)
            except AttributeError:
                pass
            try:
                self._opt_enabled.ui_update(self._opt_enabled)
            except AttributeError:
                pass
            except TypeError:
                pass
            return

        self._dir = directory
        self._filepath = os.path.join(self._dir, self.FILENAME)

        contents_corrupt = False

        try:
            if os.path.exists(self._filepath):
                with open(self._filepath, 'rt') as state_file:
                    state_data = json.load(state_file)
                    if not is_initial_load:
                        self._state_data = self._merge_states(
                                            self._state_data,
                                            state_data)
                    else:
                        self._state_data = state_data
        except json.decoder.JSONDecodeError:
            Logger.critical(
                __name__,
                'App state file is invalid, will be overwritten!')

            if not len(self._state_data):
                self._state_data = {'options': {}}

            contents_corrupt = True

        try:
            with open(self._filepath, mode='a') as state_file:
                if state_file:
                    Logger.info(
                        __name__,
                        'Set app state file to "%s"' % self._filepath)

                    self._enablable = True
                    self._opt_enabled.change(True)

            if contents_corrupt:
                self._write_state()
        except IOError:
            Logger.warning(
                __name__,
                'Failed to open "%s" to save app state' % self._filepath)

            self._enablable = False
            self._opt_enabled.change(False)

        try:
            if self._opt_enabled.ui is not None:
                self.nottreal.router(
                    'wizard',
                    'update_option',
                    option=self._opt_enabled)
        except AttributeError:
            pass

        if not is_initial_load:
            self._update_options()

    def _merge_states(self, current_state, new_state):
        """
        Merge a new state with an old one, replacing the values if
        they exist

        Arguments:
            current_state {dict} -- Current application state
            new_state {dict} -- New application state

        Returns:
            {dict} -- New state dictionary
        """
        for k, v in current_state.items():
            if k in new_state:
                if type(v) == dict:
                    self._merge_states(current_state[k], new_state[k])
                else:
                    current_state[k] = new_state[k]
        return current_state

    def _update_options(self):
        """
        Run through the application state and update the
        {WizardOption}'s based on the application state
        """
        for label, value in self._state_data['options'].items():
            if label in self._options:
                option = self._options[label]
                if option.value != value:
                    option.change(value, dont_save=True)
                    try:
                        option.ui_update(option)
                    except TypeError:
                        Logger.warning(
                            __name__,
                            'Cannot update UI for option "%s"'
                            % option.key)

    def _write_state(self):
        """
        Write the state to the file
        """
        if self._force_off or not self._opt_enabled.value:
            return

        Logger.debug(
            __name__,
            'Saving application state to "%s"' % self._filepath)
        with open(self._filepath, mode='w') as state_file:
            json.dump(self._state_data, state_file)

    def get_option(self, option):
        """
        Get an option from the state or the default value

        Arguments:
            option {WizardOption} -- Option to restore

        Returns:
            value {mixed} -- Value restored or the default option
        """
        if self._force_off or not self._opt_enabled:
            return option.default

        try:
            self._state_data['options']
        except KeyError:
            self._state_data = {}
            self._state_data['options'] = {}

        try:
            value = self._state_data['options'][option.key]
        except KeyError:
            self._state_data['options'][option.key] = option.default
            value = option.default
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

        self._options[option.key] = option
        self._state_data['options'][option.key] = option.value

        if self.ITERATIVE_SAVING:
            self._write_state()
