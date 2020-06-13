
from ..utils.log import Logger
from ..models.m_mvc import VUIState, WizardOption
from .c_abstract import AbstractController


class WizardController(AbstractController):
    """Primary controller for the Wizard window"""
    def __init__(self, nottreal, args):
        """
        Controller to manage the Wizard's manager window.

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self.state = VUIState.COMPUTING

    def ready(self):
        """
        Called when the framework is established and the controller can
        start controlling.
        """
        self.nottreal.view.wizard_window.init_ui()

        self._clear_slots_on_tab_change = False
        self.register_option(
            label=_('Clear slot tracking on tab change'),
            method=self._set_clear_slots_on_tab_change,
            default=self._clear_slots_on_tab_change)

        Logger.info(__name__, "Opening the Wizard window…")
        self.nottreal.view.wizard_window.show()

    def respond_to(self):
        """
        This class will handle "wizard" commands only.

        Returns:
            str -- Label for this controller
        """
        return 'wizard'

    def register_option(self,
                        label,
                        method,
                        opt_type=WizardOption.CHECKBOX,
                        default=False,
                        values={}):
        """
        Create an option for the user to specify

        Arguments:
            label {str} -- Label of the option
            method {method} -- Method to call with the value when
                its changed

        Keyword Arguments:
            opt_type {int} -- The type of option
                (default: {WizardOption.CHECKBOX})
            default {bool} -- Default value (default: {False})
            values {dict} -- Dictionary of values (default: {{}})
        """
        Logger.debug(__name__, 'Option "%s" registered' % label)
        option = WizardOption(
            label=label,
            method=method,
            opt_type=opt_type,
            default=default,
            values=values
        )
        self.nottreal.view.wizard_window.options.add(option)

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

        if self._clear_slots_on_tab_change:
            Logger.debug(__name__, 'Clear parameter tracking')
            self.nottreal.view.wizard_window.command.clear_saved_slots()

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
        Logger.debug(__name__, 'New state: %d' % state)

        if self.state is VUIState.SPEAKING \
                and state is not VUIState.SPEAKING:
            self.router('voice', 'stop_speaking')

        self.state = state

        if state is VUIState.NOTHING:
            self.router('output', 'now_resting')
        elif state is VUIState.COMPUTING:
            self.router('output', 'now_computing')
        elif state is VUIState.LISTENING:
            self.router('output', 'now_listening')

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
        """
        Logger.debug(__name__, 'Slot tracking on tab change: %r' % value)
        self._clear_slots_on_tab_change = value
