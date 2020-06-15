
from ..utils.log import Logger
from ..utils.init import ClassUtils
from .c_abstract import AbstractController
from ..models.m_mvc import Message, VUIState, WizardOption

from collections import deque
from subprocess import call

import abc
import threading
import time
import sys


class VoiceController(AbstractController):
    """
    Root controller for the voice synthesis systems
    
    Variables:
        DEFAULT_VOICE {str} -- Class name of the default system  
    """
    DEFAULT_VOICE = 'VoiceOutputToLog'
    def __init__(self, nottreal, args):
        """
        Controller to generate the voice of the Wizard.

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self._voice = args.voice
        self.voice_instance = None

    def ready(self):
        self._available_voices = self.available_voices()
        
        voice = self._voice[0].title() + self._voice[1:]
        if voice == 'None':
            voice = self.DEFAULT_VOICE
        else:
            voice = 'Voice' + voice
        
        self._set_voice(voice)
        self.nottreal.router(
            'wizard',
            'register_option',
            label='Voice subsystem',
            method=self._set_voice,
            opt_cat=WizardOption.CAT_OUTPUT,
            opt_type=WizardOption.SINGLE_CHOICE,
            default=voice,
            values=self._available_voices,
            order=0,
            group=10)


    def quit(self):
        """
        This class doesn't have to do anything on quit
        """
        pass

    def respond_to(self):
        """
        This class will handle "voice" and "voice_root" commands. This
        controller will be replaced as handler of "voice" commands by
        the chosen subsystem.

        Returns:
            [{str}] -- Label for this controller
        """
        return ['voice', 'voice_root']

    def relinquish(self, instance):
        """
        Relinquish control over voice signals to the right subsystem.

        Arguments:
            instance {AbstractController} -- Controller that has said
                                             it wants to be a responder
                                             for the same signals as 
                                             this controller
        Returns:
            {bool} -- True if it's the voice subsystem we're expecting
        """
        return instance == self.voice_instance

    def available_voices(self):
        return {c: self.nottreal.controllers[c].name()
                for k, c in enumerate(self.nottreal.controllers)
                if c.startswith('Voice')
                and ClassUtils.is_subclass(c, AbstractVoiceController)}

    def speak(self, text):
        """
        Respond to the "speak" button being clicked.

        Arguments:
            text {string} -- Text that should be spoken
        Return:
            {bool} -- True if the text was queued to be spoken
        """
        Logger.error(__name__, 'No voice instantiated!')
        return False

    def stop_speaking(self, clear_all=None):
        """
        Immediately cancel talking

        Arguments:
            clear_all {bool} -- {True} if any unspoken text should 
                                not be spoken also, UI configured 
                                element if {None} (Default {None}}
        Return:
            {bool} -- False
        """
        Logger.error(__name__, 'No voice instantiated!')
        return False

    def _set_voice(self, voice):
        """
        Set a voice subsystem to the used system
        
        Arguments:
            voice {str} -- Class name of the subsystem
        """
        if self.voice_instance is not None:
            self.router('voice', 'packdown')
        
        try:
            self.voice_instance = self.nottreal.controllers[voice]
            name = self.voice_instance.__class__.__name__
        except KeyError:
            try:
                self.voice_instance = \
                    self.nottreal.controllers['Voice' + voice]
                name = self.voice_instance.__class__.__name__
            except KeyError:
                tb = sys.exc_info()[2]
                raise KeyError(
                    'Unknown voice ID: "%s"' % voice).with_traceback(tb)
                return

        Logger.info(__name__, 'Setting voice to "%s"' % name)

        self.responder('voice', self.voice_instance)
        self.router('voice', 'init', args=self.args)


class AbstractVoiceController(AbstractController):
    """
    Base class that implements a simple abstract voice controller.

    Extends:
        AbstractVoiceController
    """
    def __init__(self, nottreal, args):
        """
        Base voice class that does nothing.

        Arguments:
            nottreal {} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self.append_text = False
        self.auto_listening = True

    @abc.abstractmethod
    def init(self, args):
        """
        Initialise this voice subsystem.

        Decorators:
            abc.abstractmethod

        Arguments:
            args {[str]} -- Arguments passed through for the voice
                            subsystem
        """
        self.router(
            'wizard',
            'register_option',
            label='Listening state after speech',
            opt_cat=WizardOption.CAT_OUTPUT,
            method=self._set_auto_listening,
            default=self.auto_listening)

    @abc.abstractmethod
    def packdown(self):
        """
        Packdown this voice subsystem (e.g. if the user changes
        the system used)
        
        Remember to deregister options!
        """
        self.router(
            'wizard',
            'deregister_option',
            label='Listening state after speech',
            opt_cat=WizardOption.CAT_OUTPUT)

    @abc.abstractmethod
    def name(self):
        return 'Unimplemented voice'

    def relinquish(self, instance):
        """
        Relinquish control over voice signals to the right subsystem.

        Arguments:
            instance {AbstractController} -- Controller that has said
                                             it wants to be a responder
                                             for the same signals as 
                                             this controller
        Returns:
            {bool} -- True if it's the voice subsystem we're expecting
        """
        return instance == self.nottreal.responder('voice_root').voice_instance

    @abc.abstractmethod
    def quit(self):
        """
        Shutdown the voice subsystem.
        """
        pass

    @abc.abstractmethod
    def speak(self,
              text,
              cat=None,
              id=None,
              slots=None,
              loading=False):
        """
        Produce a particular utterance.

        Decorators:
            abc.abstractmethod

        Arguments:
            text {str} -- Text to say

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
            loading {bool} -- Is a loading message
        """
        self._produce_voice(text, text, cat, id, slots)

    def _set_auto_listening(self, new_value):
        """
        After speaking, should the UI default to the VUIState.BUSY state (False) or
        the LISTENING state (True).

        Arguments:
            new_value {bool} -- New checked status
        """
        if new_value:
            Logger.debug(__name__, 'Will default to LISTENING state')
        else:
            Logger.debug(__name__, 'Will default to VUIState.BUSY state')

        self.auto_listening = new_value

    @abc.abstractmethod
    def _produce_voice(self,
                       text,
                       prepared_text,
                       cat=None,
                       id=None,
                       slots=None):
        """
        Call the voice subsystem to produce the voice. This will be
        called from the separate thread.

        You should block on this thread until the voice is spoken.

        Calls the method `send_to_recorder` to send the data to
        the recorder. If overriding this, you should to the same
        too!

        Decorators:
            abc.abstractmethod

        Arguments:
            text {str} -- Raw text from the top of the queue
            prepared_text {str} -- Text from the top of the queue
                that has been prepared by #prepare_text()

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        self.send_to_recorder(text, cat, id, slots)

    def send_to_recorder(self, text, cat=None, id=None, slots=None):
        """
        Send data to the data recorder.

        Arguments:
            text {str} -- Text from the top of the queue

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        if cat and id:
            self.router(
                'data',
                'sent_prepared_message',
                text=text,
                cat=cat,
                id=id,
                slots=slots)
        else:
            self.router('data', 'sent_raw_message', text=text)

    def stop_speaking(self, clear_all=None):
        """
        Immediately cancel talking

        Keyword Arguments:
            clear_all {bool} -- True if any unspoken text should
                not be spoken  also, UI configured element if
                {None} (Default {None}})
        Return:
            {bool} -- False
        """
        Logger.error(
            __name__,
            'Cannot cancel output on non-thread voice controller')
        return False


class ThreadedBaseVoice(AbstractVoiceController):
    """
    Base class that implements threading for calling a voice
    subsystem from a separate thread.

    Extends:
        AbstractVoiceController
    """

    def __init__(self, nottreal, args, blocking=True):
        """
        Create the thread that sends commands to the voice subsystem

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments

        Keyword Arguments:
            blocking {bool} -- Thread blocked during talking
        """
        super().__init__(nottreal, args)

        self._blocking = blocking
        self._is_speaking = False

    def init(self, args):
        """
        Create the voice thread to handle the voice subsystem

        Arguments:
            args {[str]} -- Arguments for the voice subsystem
                initiation
        """
        super().init(args)

        self._sleep_between_queue_checks = .3
        self._interrupt = threading.Event()
        self._stop_voice_loop = False
        self._text_queue = deque()

        self.append_override = Message.NO_OVERRIDE
        self._dont_append_cat_change = True
        self._clear_queue_on_interrupt = True

        self.nottreal.router(
            'wizard',
            'register_option',
            label='Clear queue on interrupt',
            opt_cat=WizardOption.CAT_WIZARD,
            method=self._set_clear_queue_on_interrupt,
            default=self._clear_queue_on_interrupt)
            
        self._voice_thread = threading.Thread(
                target=self._speak,
                args=())
        Logger.debug(__name__, 'Voice thread created')

        self._voice_thread.daemon = True
        self._voice_thread.start()

    def packdown(self):
        """
        Packdown this voice subsystem (e.g. if the user changes
        the system used)
        """
        super().packdown()
        
        self.router(
            'wizard',
            'deregister_option',
            label='Clear queue on interrupt',
            opt_cat=WizardOption.CAT_OUTPUT)

    def _set_dont_append_cat_change(self, value):
        """
        After a category change, should the append option be set
        to {False} for the first utterance,.

        Arguments:
            value {bool} -- New checked status
        """
        Logger.debug(__name__, 'Don\'t append on first message: %r' % value)
        self._dont_append_cat_change = value
        self.append_override = Message.NO_OVERRIDE

    def _set_clear_queue_on_interrupt(self, value):
        """
        Clear the queue when the speech output is interrupted

        Arguments:
            value {bool} -- New checked status
        """
        Logger.debug(__name__, 'Clear queue on interrupt: %r' % value)
        self._clear_queue_on_interrupt = value

    def category_changed(self, new_cat_id):
        """
        Report to the voice subsystem that the user has changed
        the category

        Arguments:
            new_cat_id {str} -- New category ID
        """
        if self._dont_append_cat_change:
            self.append_override = Message.FORCE_DONT_APPEND
        else:
            self.append_override = Message.NO_OVERRIDE

    def speak(self,
              text,
              cat=None,
              id=None,
              slots=None,
              loading=False):
        """
        Add the message to the queue to be spoken.

        Arguments:
            text {str} -- Text to output to the macOS say command
        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
            loading {bool} -- Is a loading message (default: False)
        Return:
            {bool} -- True if the text was queued to be spoken
        """
        self.router('wizard', 'enqueue_text', text=text)
        message = Message(
            text.strip(),
            override=self.append_override,
            cat=cat,
            id=id,
            slots=slots,
            loading=loading)
        self._text_queue.append(message)
        self.append_override = Message.NO_OVERRIDE
        return True

    def quit(self):
        """
        Interrupt the voice thread so that it comes to a graceful halt
        """
        self._stop_voice_loop = True

    def _prepare_text(self, text):
        """
        Prepare text by stripping quotes and deciding whether it
        should be shown in the wizard window

        Return:
            {(str, str)} -- Prepared text for the voice subsystem
                and text to show ({None} if should not be written
                to screen)
        """
        text = text.replace('"', '')
        return (text, text)

    def _speak(self):
        """
        Continuously process the queue of text to synthesise. Run
        this in a separate thread.
        """
        Logger.debug(__name__, 'Voice thread started')

        while self._stop_voice_loop is False:
            while not self._text_queue \
                    or (self._blocking and self._is_speaking):
                time.sleep(self._sleep_between_queue_checks)

            try:
                message = self._text_queue.popleft()
                text = message.text
                loading = message.loading
                prepared_text, text_to_show = self._prepare_text(text)

                if loading:
                    self._on_start_speaking(
                        text=text,
                        text_to_show=text_to_show,
                        state=VUIState.BUSY)
                else:
                    self._on_start_speaking(
                        text=text,
                        text_to_show=text_to_show,
                        state=VUIState.SPEAKING)

                if self._blocking:
                    self._is_speaking = True

                self._produce_voice(
                    text,
                    prepared_text,
                    message.cat,
                    message.id,
                    message.slots)

                if self._blocking:
                    self._on_stop_speaking(loading=loading)

            except Exception as e:
                Logger.critical(
                    __name__,
                    'Error generating voice: %s' % repr(e))
                raise e

        Logger.debug(__name__, 'Voice thread finished')

    def is_interrupted(self):
        return not self._interrupt.is_set()

    def wait(self, timeout):
        return self._interrupt.wait(timeout)

    def stop_speaking(self, clear_all=None):
        """
        Immediately cancel talking

        Arguments:
            clear_all {bool} -- True if any unspoken text should
                not be spoken also, UI configured element
                if {None} (Default {None}}
        Return:
            {bool} -- True
        """
        if clear_all is None:
            clear_all = self._clear_queue_on_interrupt

        if clear_all:
            self.router('wizard', 'clear_queue')
            self._text_queue.clear()
            Logger.debug(__name__, 'Queued text cleared')
        else:
            Logger.debug(__name__, 'Not clearing the queued')

        self._interrupt_voice()

        return True

    def _on_start_speaking(self,
                           text=None,
                           text_to_show=None,
                           state=VUIState.SPEAKING):
        """
        Update NottReal to denote we've started speaking

        Keyword arguments:
            text {str} -- Text currently been spoken
            text_to_show {str} -- Text currently been spoken
                (user friendly)
            state {int} -- State of the Wizard
        """
        self._is_speaking = True
        self.router('wizard', 'now_speaking', text=text)
        self.router('output', 'now_speaking', text=text_to_show, orb=state)

    def _on_stop_speaking(self, state=None, loading=False):
        """
        Update NottReal to denote we've finished speaking (will request
        the outputs to update if needed).

        Keyword arguments:
            state {int} -- State of the VUI (if external to NottReal)
        """
        self._is_speaking = False

        if not loading:
            if (state is None and self.auto_listening) \
                    or (state == VUIState.LISTENING):
                self.router(
                    'wizard',
                    'change_state',
                    state=VUIState.LISTENING)
            elif state == VUIState.BUSY:
                self.router(
                    'wizard',
                    'change_state',
                    state=VUIState.BUSY)
            else:
                self.router(
                    'wizard',
                    'change_state',
                    state=VUIState.RESTING)

    def _interrupt_voice(self):
        """
        Immediately cancel waiting (if we are waiting)
        """
        Logger.debug(__name__, 'Interrupt voice command output')
        self._interrupt.set()
        self._interrupt.clear()


class NonBlockingThreadedBaseVoice(ThreadedBaseVoice):
    """
    A threaded voice controller where the voice subsystem is
    non-blocking (i.e. it may run on separate a thread/process)
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to the voice subsystem.

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args, blocking=False)


class VoiceOutputToLog(ThreadedBaseVoice):
    """
    Output the speech to the log only.

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to the log

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self._no_waiting = False

    def init(self, args):
        super().init(args)
        self.nottreal.router(
            'wizard',
            'register_option',
            opt_cat=WizardOption.CAT_OUTPUT,
            label='Don\'t simulate talk time',
            method=self._set_no_waiting,
            default=self._no_waiting)

    def packdown(self):
        """
        Packdown this voice subsystem (e.g. if the user changes
        the system used)
        """
        super().packdown()
        
        self.router(
            'wizard',
            'deregister_option',
            label='Don\'t simulate talk time',
            opt_cat=WizardOption.CAT_OUTPUT)

    def name(self):
        return 'Output to log'

    def _set_no_waiting(self, value):
        """
        Change the artificial waiting for the delay in the
        generation of text to simulate speech.

        Arguments:
            value {bool} -- New checked status
        """
        Logger.debug(__name__, 'Instant printing: %r' % value)
        self._no_waiting = value

    def _produce_voice(self,
                       text,
                       prepared_text,
                       cat=None,
                       id=None,
                       slots=None):
        """
        Receive the text to produce, output it to the log,
        and block if desired.

        Arguments:
            text {str} -- Text from the manager window
            prepared_text {str} -- Text from the manager
                window (not difference to text)

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        self.send_to_recorder(text, cat, id, slots)
        Logger.info(__name__, 'Now saying "%s"' % text)

        if not self._no_waiting:
            timeout = len(text)/10
            super().wait(timeout)


class VoiceShellCmd(ThreadedBaseVoice):
    """
    Call a command via the shell to generate the voice.

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to the external shell

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

    def init(self, args):
        """
        Load the configuration.
        """
        super().init(args)

        self._cfg = self.nottreal.config.cfg()

        self._command_speak = self._cfg.get(
            'VoiceShellCmd',
            'command_speak')
        self._command_interrupt = self._cfg.get(
            'VoiceShellCmd',
            'command_interrupt')

    def name(self):
        return 'Shell command'

    def _prepare_text(self, text):
        """
        Construct the command for the shell execution and
        prepare the text for display

        Arguments:
            text {str} -- Text from the Wizard manager window

        Return:
            {(str, str)} -- Command and the prepared text
                ({None} if should not be written to screen)
        """
        cmd_text = text.replace('"', '')

        return (self._command_speak % cmd_text, text)

    def _produce_voice(self,
                       text,
                       prepared_text,
                       cat=None,
                       id=None,
                       slots=None):
        """
        Receive the text (which should be a command), and then
        call it.

        Arguments:
            text {str} -- Text to record as being produced
            prepared_text {str} -- Command to call through a shell

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        self.send_to_recorder(text, cat, id, slots)
        Logger.debug(__name__, 'Calling %s' % prepared_text)
        call(prepared_text, shell=True)

    def _interrupt_voice(self):
        """
        Immediately cancel waiting (if we are waiting)
        """
        if len(self._command_interrupt) > 0:
            return call(self._command_interrupt, shell=True)
        else:
            Logger.error('voice', 'No interrupt command supplied')
