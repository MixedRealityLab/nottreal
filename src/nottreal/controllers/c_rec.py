
from ..utils.log import Logger
from ..models.m_mvc import VUIState, WizardOption
from .c_abstract import AbstractController


class RecognitionController(AbstractController):
    def __init__(self, nottreal, args):
        """
        Controller to do speech to text recognition

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionController, self).__init__(nottreal, args)

        if args.recognition == 'None':
            self._recognition = None
        else:
            self._recognition = args.recognition
        self._recognitionInstance = None

        self.is_recognising = False

    def ready_order(self, responder=None):
        """
        We should be readied early
        
        Arguments:
            responder {str} -- Will only work for the
                               {recognition_root}
                               responder
        """
        return 20 if responder == 'recognition_root' else -1

    def ready(self, responder=None):
        """
        Load the voice recognition subsystem if enabled
        
        Arguments:
            responder {str} -- Will only work for the
                               {recognition_root} responder
        """
        if responder != 'recognition_root':
            return
            
        if self._recognition is not None:
            name = 'Recognition%s%s' % \
                   (self._recognition[0].title(), self._recognition[1:])

            try:
                self._recognitionInstance = self.nottreal.controllers[name]
            except KeyError:
                Logger.critical(
                    __name__,
                    'Could not find recognition controller "%s"' % name)
                return

            Logger.info(__name__, 'Setting recognition to "%s"' % name)

            self.responder('recognition', self._recognitionInstance)
            self.router('recognition', 'init', args=self.args)
        else:
            Logger.info(__name__, 'No voice recognition enabled')

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
        return instance == self._recognitionInstance

    def enabled(self):
        """
        Whether voice recognition is enabled

        Returns:
            {bool}
        """
        return False

    def now_listening(self):
        """Does nothing as no recogniser is set"""
        pass

    def now_not_listening(self):
        """Does nothing as no recogniser is set"""
        pass

    def start_recognising(self):
        """Does nothing as no recogniser is set"""
        pass

    def stop_recognising(self):
        """Does nothing as no recogniser is set"""
        pass


class AbstractRecognition(AbstractController):
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
        super(AbstractRecognition, self).__init__(nottreal, args)

    def init(self, args):
        """
        Set up the speech to text library by identifying the microphone
        """
        self._callbacks = []

        self._recognition_during_listening = True
        self.nottreal.router(
            'wizard',
            'register_option',
            opt_cat=WizardOption.CAT_INPUT,
            label='Recognition during listening state only',
            method=self._set_recognition_during_listening,
            default=self._recognition_during_listening,
            group=1)

    def ready_order(self, responder=None):
        """
        Voice controllers are readied by the {RecognitionController}
        
        Returns:
            -1
        """
        return -1

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
        Logger.debug(__name__, 'Recognise only during listening: %r' % value)
        self._recognition_during_listening = value

        if not value and not self.is_recognising:
            self.start_recognising()
        elif value \
                and self.is_recognising \
                and self.nottreal.controllers['WizardController'].state \
                is not VUIState.LISTENING:
            self.stop_recognising()

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
        if self._recognition_during_listening and \
                self.is_recognising is False:
            self.start_recognising()

    def now_not_listening(self):
        """
        The VUI is not in the listening state. Stop listening if we're
        listening and we should only listen in the listening state.
        """
        if self._recognition_during_listening and \
                self.is_recognising is True:
            self.stop_recognising()

    def start_recognising(self):
        """
        Start voice recognition
        """
        Logger.error(__name__, 'No voice recognition library instantiated!')
        self.is_recognising = True

    def stop_recognising(self):
        """
        Immediately cancel recognition

        Returns:
            {bool} -- False
        """
        Logger.error(__name__, 'No voice recognition library instantiated!')
        self.is_recognising = False
