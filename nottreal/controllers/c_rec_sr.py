
from ..utils.log import Logger
from ..models.m_mvc import WizardAlert
from .c_rec import AbstractRecognitionController

import importlib
import time
import threading


class SRRecognition(AbstractRecognitionController):
    """
    Base voice recognition library that transcribes input in a
    background thread and displays the results

    Based on `speech_recognition' library

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
        super(SRRecognition, self).__init__(nottreal, args)

        self._stop_thread = None
        self._lock = True
        self.config = nottreal.config.cfg()

        Logger.debug(__name__, 'Loading "speech_recognition" module')
        self.sr = importlib.import_module('speech_recognition')

    def name(self):
        return 'Unimplemented recogniser'

    def packdown(self, on_complete=None):
        """
        Packdown the current voice recognition system and
        (optionally) call a method once done.

        Keyword arguments:
            on_complete {func} -- Method to call on complete
        """
        self.stop_recognising(on_complete=on_complete)

    def enabled(self):
        """
        Whether voice recognition is enabled

        Returns:
            {bool}
        """
        return True

    def start_recognising(self):
        """
        Start voice recognition thread
        """
        if self._stop_thread is not None \
                and self._stop_thread.is_alive():
            Logger.debug(
                __name__,
                'Waiting for previous shutdown of recognising')
            time.sleep(.5)
            return self.start_recognising()

        Logger.info(__name__, 'Started listening for voice recognition')

        self.rec = self.sr.Recognizer()
        self._stop_recognising = self.rec.listen_in_background(
            self.nottreal.responder('input').source,
            self.process_audio)

        super().start_recognising()

    def stop_recognising(self, on_complete=None):
        """
        Immediately cancel recognition and (optionally) call a
        method once done.

        Keyword arguments:
            on_complete {func} -- Method to call on complete

        Returns:
            {bool} -- False
        """
        Logger.info(__name__, 'Finished listening for voice recognition')

        try:
            self._stop_thread = threading.Thread(
                    target=self._stop_recognising,
                    args=())
            self._stop_thread.daemon = True
            self._stop_thread.start()

            super().stop_recognising(on_complete)
        except AttributeError:
            Logger.debug(__name__, 'Seemingly not recognising at the moment')

    def alert_recogniser_error(self, message):
        """
        Show the Wizard that we have an error with the recogniser.

        Argument:
            message {str} -- Specific error message
        """
        alert = WizardAlert(
            'Error transcribing voice',
            ('An error has occurred with the voice recogniser "%s":\n\n%s\n\n'
                + 'Ensure you have specified valid credentials in '
                + '"settings.cfg".')
            % (self.name(), message),
            WizardAlert.LEVEL_ERROR)

        self.router('wizard', 'show_alert', alert=alert)


class RecognitionGoogleSpeech(SRRecognition):
    """
    Use the deprecated Google Speech Recognition API for recognition

    This should not be used, it is only included for
    testing/development purposes.
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionGoogleSpeech, self).__init__(nottreal, args)

    def name(self):
        return 'Google Speech Recognition'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Google for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        key = self.config.get(
            'Recognition',
            'google_speech_recognition_api_key')
        language = self.config.get(
            'Recognition',
            'google_speech_recognition_language')

        if len(key) == 0:
            key = None

        try:
            self.recognised_words(
                rec.recognize_google(
                    audio,
                    key=key,
                    language=language))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Google: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionGoogleCloud(SRRecognition):
    """
    Use Google Cloud Speech-to-Text for recognition
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionGoogleCloud, self).__init__(nottreal, args)

    def name(self):
        return 'Google Text-to-Speech'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Google for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        credentials_json = self.config.get(
            'Recognition',
            'google_cloud_stt_credentials')
        language = self.config.get(
            'Recognition',
            'google_cloud_stt_language')

        try:
            self.recognised_words(
                rec.recognize_google_cloud(
                    audio,
                    credentials_json=credentials_json,
                    language=language))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Google: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionWitai(SRRecognition):
    """
    Use Wit.ai for recognition
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionWitai, self).__init__(nottreal, args)

    def name(self):
        return 'Wit.ai'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Wit.ai for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        key = self.config.get(
            'Recognition',
            'witai_api_key')

        try:
            self.recognised_words(
                rec.recognize_wit(
                    audio,
                    key=key))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Wit.ai: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionBing(SRRecognition):
    """
    Use the Microsoft Bing Speech API
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionBing, self).__init__(nottreal, args)

    def name(self):
        return 'Microsoft Bing'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Microsoft for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        key = self.config.get(
            'Recognition',
            'bing_api_key')
        language = self.config.get(
            'Recognition',
            'bing_language')

        try:
            self.recognised_words(
                rec.recognize_bing(
                    audio,
                    key=key,
                    language=language))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Microsoft: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionAzure(SRRecognition):
    """
    Use the Microsoft Azure Speech API
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionAzure, self).__init__(nottreal, args)

    def name(self):
        return 'Microsoft Azure'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Microsoft for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        key = self.config.get(
            'Recognition',
            'azure_api_key')
        language = self.config.get(
            'Recognition',
            'azure_language')

        try:
            self.recognised_words(
                rec.recognize_azure(
                    audio,
                    key=key,
                    language=language))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Microsoft: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionLex(SRRecognition):
    """
    Use the Amazon Lex API
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionLex, self).__init__(nottreal, args)

    def name(self):
        return 'Amazon Lex'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Amazon for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        bot_name = self.config.get(
            'Recognition',
            'lex_bot_name')
        bot_alias = self.config.get(
            'Recognition',
            'lex_bot_alias')
        user_id = self.config.get(
            'Recognition',
            'lex_user_id')
        access_key_id = self.config.get(
            'Recognition',
            'lex_access_key_id')
        secret_access_key = self.config.get(
            'Recognition',
            'lex_secret_access_key')
        region = self.config.get(
            'Recognition',
            'lex_region')

        if len(access_key_id) == 0:
            access_key_id = None
        if len(secret_access_key) == 0:
            secret_access_key = None
        if len(region) == 0:
            region = None

        try:
            self.recognised_words(
                rec.recognize_lex(
                    audio,
                    bot_name=bot_name,
                    bot_alias=bot_alias,
                    user_id=user_id,
                    access_key_id=access_key_id,
                    secret_access_key=secret_access_key,
                    region=region))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Amazon: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionHoundify(SRRecognition):
    """
    Use Houndify for recognition
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionHoundify, self).__init__(nottreal, args)

    def name(self):
        return 'Houndify'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Houndify for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        client_id = self.config.get(
            'Recognition',
            'houndify_client_id')
        client_key = self.config.get(
            'Recognition',
            'houndify_client_key')

        try:
            self.recognised_words(
                rec.recognize_azure(
                    audio,
                    client_id=client_id,
                    client_key=client_key))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Houndify: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionIBM(SRRecognition):
    """
    Use IBM Speech to Text API for recognition
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionIBM, self).__init__(nottreal, args)

    def name(self):
        return 'IBM Watson'

    def process_audio(self, rec, audio):
        """
        Send some audio off to IBM for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        username = self.config.get(
            'Recognition',
            'ibm_username')
        password = self.config.get(
            'Recognition',
            'ibm_password')
        language = self.config.get(
            'Recognition',
            'ibm_password')

        try:
            self.recognised_words(
                rec.recognize_ibm(
                    audio,
                    username=username,
                    password=password,
                    language=language))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from IBM: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))


class RecognitionTensorflow(SRRecognition):
    """
    Use Tensowflow for recognition
    """

    def __init__(self, nottreal, args):
        """
        Create the thread that sends audio and receives responses

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super(RecognitionTensorflow, self).__init__(nottreal, args)

    def name(self):
        return 'Tensorflow'

    def process_audio(self, rec, audio):
        """
        Send some audio off to Tensorflow for recognition

        Arguments:
            rec {speecrecognition.Recognizer} -- Recognizer instance
            audio {speecrecognition.AudioData} -- Some audio data
        """
        tensor_graph = self.config.get(
            'Recognition',
            'tensor_graph')
        tensor_label = self.tensor_label.get(
            'Recognition',
            'tensor_label')

        try:
            self.recognised_words(
                rec.recognize_tensorflow(
                    audio,
                    tensor_graph=tensor_graph,
                    tensor_label=tensor_label))
        except self.sr.UnknownValueError:
            Logger.debug(
                __name__,
                'No recognised words'
            )
        except self.sr.RequestError as e:
            Logger.error(
                __name__,
                'Error retrieving results from Tensorflow: %s' % str(e)
            )
            self.alert_recogniser_error(str(e))
