
from ..utils.log import Logger
from .c_rec import AbstractRecognition

import importlib
import numpy


class SRRecognition(AbstractRecognition):
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

        self.config = nottreal.config.cfg()

    def init(self, args):
        """
        Set up the speech to text library
        """
        super().init(args)

        Logger.debug(__name__, 'Loading "speech_recognition" module')
        self.sr = importlib.import_module('speech_recognition')

        self.is_recognising = False

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
        Logger.info(__name__, 'Start listening for voice recognition')
        self.is_recognising = True

        self.rec = self.sr.Recognizer()
        self._stop_recognising = self.rec.listen_in_background(
            self.nottreal.responder('input').source,
            self.process_audio)

    def _start_recognising(self):
        """
        Start voice recognition (run on a separate thread!)
        """
        Logger.info(__name__, 'Start listening for voice recognition')

        self.parent.nottreal.router(
            'input',
            'register_data_callback',
            name='recognition',
            method=self._parse_data)

    def _parse_data(self, indata, frames, time, status):
        volume_norm = numpy.linalg.norm(indata) * 10
        if volume_norm < self.GAP_SIZE_THRESHOLDS:
            if self._breached_threshold is None:
                self._breached_threshold = \
                    time.currentTime + self.GAP_SIZE_SECS
            elif time.currentTime > self._breached_threshold:
                print('finally')
        else:
            self._breached_threshold = None

    def stop_recognising(self):
        """
        Immediately cancel recognition

        Returns:
            {bool} -- False
        """
        Logger.info(__name__, 'Finished listening for voice recognition')
        self.is_recognising = False
        self._stop_recognising()


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
