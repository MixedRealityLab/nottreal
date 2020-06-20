
from ..utils.log import Logger
from ..models.m_mvc import VUIState, WizardOption
from ..models.m_tsv import TSVModel
from .c_abstract import AbstractController


class WizardController(AbstractController):
    """
    Primary controller for the Wizard window

    Variables:
        DEFAULT_DIRECTORY {str} -- Default configuration directory
    """
    DEFAULT_DIRECTORY = 'cfg'

    def __init__(self, nottreal, args):
        """
        Controller to manage the Wizard's manager window.

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self._dir = args.config_dir
        if self._dir is None:
            self._dir = self.DEFAULT_DIRECTORY

    def init_config(self):
        self._set_config_directory(self._dir, is_initial_load=True)

    def ready(self):
        """
        Called when the framework is established and the controller can
        start controlling.
        """
        self.state = VUIState.BUSY
        self.recogniser_state = False
        self.have_recognised_words = False

        self.nottreal.view.wizard_window.init_ui()

        self.nottreal.view.wizard_window.set_data(self.data)
        self.register_option(
            option=WizardOption(
                key=__name__ + '.config_dir',
                label='Select config directory…',
                category=WizardOption.CAT_CORE,
                choose=WizardOption.CHOOSE_DIRECTORY,
                method=self._set_config_directory,
                default=self._dir,
                restorable=False))

        self._opt_slots_on_tab_change = self.register_option(
            option=WizardOption(
                key=__name__ + '.slots_tab_change',
                label='Clear slot tracking on tab change',
                category=WizardOption.CAT_WIZARD,
                method=self._set_clear_slots_on_tab_change,
                default=False,
                restorable=True))

        Logger.debug(__name__, "Opening the Wizard window…")
        self.nottreal.view.wizard_window.show()

    def _set_config_directory(self, directory, is_initial_load=False):
        """
        Load some data from the directory and update the UI

        Arguments:
            directory {str} -- New configuration directory

        Keyword arguments:
            is_initial_load {bool} -- Is the initial load of the app
        """
        self.nottreal.config.update(directory)

        self.data = TSVModel(directory)

        try:
            self.nottreal.view.wizard_window.set_title(directory)
            self.nottreal.view.wizard_window.set_data(self.data)
        except AttributeError:
            pass

        try:
            self.router(
                'appstate',
                'set_directory',
                directory=directory,
                is_initial_load=is_initial_load)
        except AttributeError:
            pass

            Logger.info(
                __name__,
                'Configuration directory set to "%s"' % directory)

    def respond_to(self):
        """
        This class will handle "wizard" commands only.

        Returns:
            str -- Label for this controller
        """
        return 'wizard'

    def register_option(self, option):
        """
        Create an option for the user to specify

        Arguments:
            option {WizardOption} -- Wizard option to set

        Returns:
            {WizardOption}
        """
        self.nottreal.view.wizard_window.menu.add_option(option)
        Logger.debug(__name__, 'Option "%s" registered' % option.key)
        return option

    def update_option(self, option):
        """
        Create an option for the user to specify

        Arguments:
            option {WizardOption} -- Option to update
            new_value {mixed}     -- New value
        """
        try:
            option.ui_update(option)
            Logger.debug(__name__, 'Option "%s" updated' % option.key)
        except TypeError:
            Logger.error(
                __name__,
                'Option not updatable in UI: "%s"' % option.key)

    def deregister_option(self, option):
        """
        Remove an option for the user

        Arguments:
            option {str}    -- Option to deregister
        """
        self.nottreal.view.wizard_window.menu.remove_option(option)
        Logger.debug(__name__, 'Option "%s" deregistered' % option.key)

    def speak_text(self,
                   text,
                   cat=None,
                   id=None,
                   slots={},
                   loading=False):
        """
        Pass the text onward to the voice controller. This should
        be called from the Wizard window via the router.

        Arguments:
            text {str} -- Text to speak

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
            loading {bool} -- Is a loading message
        """
        for name, value in slots.items():
            self.nottreal.view.wizard_window.slot_history.add(name, value)

        self.router(
            'voice',
            'speak',
            text=text,
            cat=cat,
            id=id,
            slots=slots,
            loading=loading)

    def tab_changed(self, new_tab):
        """
        Called from the Wizard window when the tab view changes

        Arguments:
            new_tab {str} -- New tab/category ID
        """
        self.router('voice', 'category_changed', new_cat_id=new_tab)

        if self._opt_slots_on_tab_change.value:
            Logger.debug(__name__, 'Clear parameter tracking')
            self.nottreal.view.wizard_window.command.clear_saved_slots()

    def data_recording_enabled(self, state):
        """
        Show the pre-scripted data recording messages.

        Arguments:
            state {bool} -- {True} if data recording is enabled
        """
        if state:
            self.nottreal.view.wizard_window.command.log_msgs.show()
        else:
            self.nottreal.view.wizard_window.command.log_msgs.hide()

    def recognition_enabled(self, state):
        """
        Show the recognised words list because a valid recogniser
        has been enabled. Alternatively, will hide the list if
        a non-working recogniser has been set (unless there
        are transcribed words in the list).

        Arguments:
            state {bool} -- {True} if a working recogniser has been
                            enabled
        """
        if self.have_recognised_words:
            self.recogniser_state = state
            return

        if state and not self.recogniser_state:
            self.nottreal.view.wizard_window.toggle_recogniser()
        elif not state and self.recogniser_state:
            self.nottreal.view.wizard_window.toggle_recogniser()

        self.recogniser_state = state

    def log_message(self, id, text):
        """
        Log a message to the data file

        Arguments:
            id {str} -- ID of the message to log
            text {str} -- Test of the message to log
        """
        try:
            self.router('data', 'custom_event', id=id, text=text)
        except Exception as e:
            Logger.error(__name__, 'Error filing log message: %s' % str(e))

    def now_speaking(self, text):
        """
        Mark some text as now being spoken (and so should be removed
        from the queue).

        Arguments:
            text {str} -- Text that is queued to be spoken and is
                no longer queued.
        """
        self.nottreal.view.wizard_window.msg_queue.remove(text)
        self.nottreal.view.wizard_window.msg_history.add(text)
        self.change_state(VUIState.SPEAKING)

    def change_state(self, state):
        """
        Change the state of the VUI

        Arguments:
            state {int} -- New {VUIState}
        """
        Logger.debug(__name__, 'New VUI state: %s' % VUIState.str(state))

        self.state = state

        if state is VUIState.RESTING:
            self.router('output', 'now_resting')
            self.router('recognition', 'now_not_listening')
        elif state is VUIState.BUSY:
            self.router('output', 'now_computing')
            self.router('recognition', 'now_not_listening')
        elif state is VUIState.LISTENING:
            self.router('output', 'now_listening')
            self.router('recognition', 'now_listening')

    def stop_speaking(self):
        """
        Immediately cancel talking and optionally clear the queue based
        on runtime option.
        """
        self.router('voice', 'stop_speaking')

    def enqueue_text(self, text):
        """
        Mark some text as queued to be spoken.

        Arguments:
            text {str} -- Text that is queued to be spoken
        """
        self.nottreal.view.wizard_window.msg_queue.add(text)

    def clear_queue(self):
        """
        Clear the message queue
        """
        self.nottreal.view.wizard_window.msg_queue.clear()

    def recognised_words(self, words):
        """
        Some words have been automatically recognised and should be
        shown in the UI

        Argument:
            words {str} -- Recognised words
        """
        self.nottreal.view.wizard_window.recognised_words.add(words)
        self.have_recognised_words = True

    def quit(self):
        """
        Close and quit the Wizard window if it still exists.
        """
        self.nottreal.view.wizard_window.close()

    def _set_clear_slots_on_tab_change(self, value):
        """
        Change whether to clear parameter tracking on tab change

        Arguments:
            value {bool} -- New checked status

        Return:
            {bool} -- Always {True}
        """
        Logger.info(
            __name__,
            'Set resetting of slot tracking on tab change to %r' % value)
        return True
