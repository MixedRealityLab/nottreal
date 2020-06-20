
from ..utils.log import Logger
from ..utils.init import ClassUtils
from ..models.m_mvc import VUIState, WizardOption
from .c_abstract import AbstractController

import abc
import sys


class RecognitionController(AbstractController):
    DEFAULT_RECOGNISER = 'RecognitionNone'

    def __init__(self, nottreal, args):
        """
        Controller to do speech to text recognition

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionController, self).__init__(nottreal, args)

        self.previous_instance = None
        self._recogniser = args.recognition
        self.recogniser_instance = None

    def ready_order(self, responder=None):
        """
        We should be readied early

        Arguments:
            responder {str} -- Will only work for the
                               {recognition_root}
                               responder
        """
        return 150 if responder == 'recognition_root' else -1

    def ready(self, responder=None):
        """
        Load the voice recognition subsystem if enabled

        Arguments:
            responder {str} -- Will only work for the
                               {recognition_root} responder
        """
        if responder != 'recognition_root':
            return

        Logger.debug(__name__, 'Setting up voice recognition')

        if self._recogniser is None:
            recogniser = self.DEFAULT_RECOGNISER
            restore = True
        else:
            recogniser = 'Recognition' \
                         + self._recogniser[0].title() + self._recogniser[1:]
            restore = False

        self._available_recognisers = self.available_recognisers()
        if not self.args.dev and recogniser != 'RecognitionGoogleSpeech':
            del self._available_recognisers['RecognitionGoogleSpeech']

        self._opt_recogniser = WizardOption(
                key=__name__ + '.recogniser',
                label='Recogniser',
                method=self._set_recogniser,
                category=WizardOption.CAT_INPUT,
                choose=WizardOption.CHOOSE_SINGLE_CHOICE,
                default=recogniser,
                values=self._available_recognisers,
                order=0,
                group='recognition',
                restorable=True,
                restore=restore)
        self.nottreal.router(
            'wizard',
            'register_option',
            option=self._opt_recogniser)

        self._set_recogniser(self._opt_recogniser.value)

    def quit(self):
        """
        This class doesn't have to do anything on quit
        """
        pass

    def respond_to(self):
        """
        This class will handle "recognition" and "recognition_root"
        commands. This controller will be replaced as handler of
        "recognition" commands by the chosen subsystem.

        Returns:
            [{str}] -- Label for this controller
        """
        return ['recognition', 'recognition_root']

    def relinquish(self, instance):
        """
        Relinquish control over speech to text signals to the right
        subsystem.

        Arguments:
            instance {AbstractController} -- Controller that has
                said it wants to be a responder for the same signals
                as this controller.
        Returns:
            {bool} -- True if it's the Recognition subsystem we're
                      expecting
        """
        return instance == self.recogniser_instance

    def enabled(self):
        """
        Whether voice recognition is enabled

        Returns:
            {bool}
        """
        return True

    def available_recognisers(self):
        return {c: self.nottreal.controllers[c].name()
                for k, c in enumerate(self.nottreal.controllers)
                if c.startswith('Recognition')
                and ClassUtils.is_subclass(c, AbstractRecognitionController)}

    def now_listening(self):
        """Does nothing as no recogniser is set"""
        Logger.warning(__name__, 'No voice recognition library instantiated!')
        pass

    def now_not_listening(self):
        """Does nothing as no recogniser is set"""
        Logger.warning(__name__, 'No voice recognition library instantiated!')
        pass

    def start_recognising(self):
        """Does nothing as no recogniser is set"""
        Logger.warning(__name__, 'No voice recognition library instantiated!')
        pass

    def stop_recognising(self):
        """Does nothing as no recogniser is set"""
        Logger.warning(__name__, 'No voice recognition library instantiated!')
        pass

    def _set_recogniser(self, recogniser):
        """
        Set a recognition subsystem to the used system

        Arguments:
            recogniser {str} -- Class name of the subsystem

        Return:
            {bool} -- {True} if the recogniser was changed
        """
        Logger.info(
            __name__,
            'Set voice recognition to "%s"' % recogniser)

        previous_instance = self.recogniser_instance
        try:
            self.recogniser_instance = self.nottreal.controllers[recogniser]
        except KeyError:
            try:
                classname = 'Recognition' + recogniser
                self.recogniser_instance = self.nottreal.controllers[classname]
            except KeyError:
                tb = sys.exc_info()[2]
                raise KeyError(
                    'Unknown recognition ID: "%s"' % recogniser) \
                    .with_traceback(tb)
                return False

        if previous_instance is not None:
            was_recognising = previous_instance.is_recognising()
        else:
            was_recognising = False

        if was_recognising:
            self.next_recogniser = recogniser
            self.router(
                'recognition',
                'packdown',
                on_complete=self._finish_setting_recogniser)
        else:
            self._finish_setting_recogniser(restart_recognising=False)

        return True

    def _finish_setting_recogniser(self, restart_recognising=True):
        """
        Set a recognition subsystem to the used system

        Keyword arguments:
            restart_recognising {bool -- Restart recognition
        """
        self.responder('recognition', self.recogniser_instance)
        self.router('recognition', 'init', args=self.args)
        self.router('recognition', 'ready')


class AbstractRecognitionController(AbstractController):
    """
    Base voice recognition library that handles the mic and setup

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(AbstractRecognitionController, self).__init__(nottreal, args)

    def init(self, args):
        """
        Set up the speech to text library by identifying the microphone
        """
        self._callbacks = []

        self._is_recognising = False

        self._opt_rec_during_listening = WizardOption(
            key=__name__ + '.during_listening',
            label='Recognition during listening state only',
            method=self._set_recognition_during_listening,
            category=WizardOption.CAT_INPUT,
            default=True,
            order=2,
            group='recognition',
            restorable=True)
        self.nottreal.router(
            'wizard',
            'register_option',
            option=self._opt_rec_during_listening)

        self._set_recognition_during_listening(
            self._opt_rec_during_listening.value)

    def ready(self, responder=None):
        """
        Ensure the recognised words list is in the UI
        """
        self.router(
            'wizard',
            'recognition_enabled',
            state=True)

    def packdown(self, on_complete=None):
        """
        Packdown the current voice recognition system and
        (optionally) call a method once done.

        Keyword arguments:
            on_complete {func} -- Method to call on complete
        """
        self.stop_recognising(on_complete=on_complete)

    @abc.abstractmethod
    def name(self):
        return 'Unimplemented recogniser'

    def relinquish(self, instance):
        """
        Relinquish control over recognition signals to the right subsystem.

        Arguments:
            instance {AbstractController} -- Controller that has said
                                             it wants to be a responder
                                             for the same signals as
                                             this controller
        Returns:
            {bool} -- True if it's the recognition subsystem we're
                      expecting
        """
        return instance == \
            self.nottreal.responder('recognition_root').recogniser_instance

    def is_recognising(self):
        return self._is_recognising

    def _set_recognition_during_listening(self, value):
        """
        Change whether to voice recognition runs continuously ({False})
        or during listening state ({True})

        Start recognising if the Wizard wants to always recognise and
        we're not. Stop recognising if the Wizard wants to only
        recognise during the listening state and we're not in it.

        Arguments:
            value {bool} -- New checked status
        """
        Logger.debug(
            __name__,
            'Set recognition only while \'listening\' to %r' % value)

        if not self._opt_rec_during_listening.value \
                and not self.is_recognising():
            self.router('recognition', 'start_recognising')
        elif self._opt_rec_during_listening.value \
                and self.is_recognising() \
                and self.nottreal.controllers['WizardController'].state \
                is not VUIState.LISTENING:
            self.router('recognition', 'stop_recognising')

        return True

    def recognised_words(self, words):
        Logger.debug(
            __name__,
            'Recognised the words: "%s"' % words
        )
        self.router(
            'wizard',
            'recognised_words',
            words=words
        )
        self.router(
            'data',
            'transcribed_text',
            text=words)

    def now_listening(self):
        """
        The VUI is in the listening state. Start listening if we're not
        already.
        """
        if self._opt_rec_during_listening.value and \
                not self.is_recognising():
            self.start_recognising()

    def now_not_listening(self):
        """
        The VUI is not in the listening state. Stop listening if we're
        listening and we should only listen in the listening state.
        """
        if self._opt_rec_during_listening.value and \
                self.is_recognising():
            self.stop_recognising()

    def start_recognising(self):
        """
        Start voice recognition
        """
        self._is_recognising = True

    def stop_recognising(self, on_complete=None):
        """
        Immediately cancel recognition and (optionally) call a
        method once done.

        Keyword arguments:
            on_complete {func} -- Method to call on complete

        Returns:
            {bool} -- False
        """
        self._is_recognising = False
        if on_complete is not None:
            on_complete()


class RecognitionNone(AbstractRecognitionController):
    """
    No voice recognition library used

    Extends:
        AbstractRecognitionController
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionNone, self).__init__(nottreal, args)

    def name(self):
        return 'None'

    def ready(self, responder=None):
        """
        Ensure the recognised words list isn't in the UI
        """
        self.router(
            'wizard',
            'recognition_enabled',
            state=False)
