
from ..utils.log import Logger
from ..models.m_mvc import WizardOption
from .c_abstract import AbstractController

from speech_recognition import Microphone

import audioop
import pyaudio
import threading


class InputController(AbstractController):
    """
    Handle input source data

    Extends:
        AbstractController

    """
    def __init__(self, nottreal, args):
        """
        Controller to listen to a microphone and send
        data around the application

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self._num_callbacks = 0
        self._callbacks_volume = {}

        self.source = Microphone()
        self._pyaudio = self.source.pyaudio_module
        self._thread = None

        self.devices = {}
        audio = self._pyaudio.PyAudio()
        for i in range(audio.get_device_count()):
            device = audio.get_device_info_by_index(i)
            if device['maxInputChannels'] > 0:
                self.devices[i] = device['name']

        audio.terminate()

        Logger.debug(
            __name__,
            'Found input sources: %s' % str(self.devices)
            )

    def respond_to(self):
        """
        This class will handle "input" commands

        Returns:
            str -- Label for this controller
        """
        return 'input'

    def ready(self):
        """Set the default input source"""

        self._vol_sensitivity = self.nottreal.config.cfg().getint(
            'Input',
            'sensitivity')

        audio = self._pyaudio.PyAudio()
        device = audio.get_default_input_device_info()['index']

        self.nottreal.router(
            'wizard',
            'register_option',
            option=WizardOption(
                label='Input source',
                method=self.set_device,
                opt_cat=WizardOption.CAT_INPUT,
                opt_type=WizardOption.SINGLE_CHOICE,
                default=device,
                values=self.devices,
                group=0))

        self.set_device(device)
        audio.terminate()

    def set_device(self, device):
        """
        Set a microphone/input source

        Arguments:
            device {int} -- Index of the device from {self.devices}
        """
        Logger.info(
            __name__,
            'Set input source to "%s"' % self.devices[device])

        self.selected_device = device
        self._swap_to_device = device

    def register_volume_callback(self, name, method):
        """
        Register a callback for the volume level

        Arguments:
            name {str} -- Name of the callback
            method {method} -- Method to call back (must take on param)
        """
        self._callbacks_volume[name] = method

        self._num_callbacks = len(self._callbacks_volume)
        if self._num_callbacks == 1:
            self._start_listening()

    def deregister_volume_callback(self, name):
        """
        Remove a registered callback for the volume level

        Arguments:
            name {str} -- Name of the callback
        """
        try:
            del self._callbacks_volume[name]
            self._num_callbacks -= 1

            if self._num_callbacks == 0:
                self._stop_listening()
        except KeyError:
            pass

    def _start_listening(self):
        """
        Starts the thread for listening to the input source.
        """
        if self._thread is not None:
            Logger.error(__name__, 'Already listening on another thread')
            return

        self._hot_mic = True
        self._thread = threading.Thread(target=self._listening_loop)
        self._thread.daemon = True
        self._thread.start()

    def _stop_listening(self):
        """
        Stop listening.
        """
        self._hot_mic = False

    def _listening_loop(self):
        """
        Listen to the selected audio source. This should be
        called on a separate thread!
        """
        Logger.info(__name__, 'Listening to the input source')

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        audio = self._pyaudio.PyAudio()
        stream = audio.open(
                        input_device_index=self._swap_to_device,
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        self._swap_to_device = None

        while self._hot_mic \
                and self._num_callbacks > 0 \
                and self._swap_to_device is None:

            data = stream.read(CHUNK, exception_on_overflow=False)
            max_volume = audioop.max(data, 2) / self._vol_sensitivity

            for method in self._callbacks_volume.values():
                method(max_volume)

        Logger.info(__name__, 'Stopped listening to the input source')
        stream.stop_stream()
        stream.close()
        audio.terminate()

        if self._swap_to_device is not None:
            return self._listening_loop()

        self._thread = None
