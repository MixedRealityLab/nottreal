
from ..utils.log import Logger
from ..models.m_mvc import WizardOption
from .c_abstract import AbstractController

import numpy
import sounddevice as sd
import threading


class SDController(AbstractController):
    """
    Handle microphone data through "sounddevice".

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

        self._thread = None

        devices = sd.query_devices()
        self.devices = {}
        for key, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                self.devices[key] = device['name']

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
        self.set_device(sd.default.device[0])

    def set_device(self, device):
        """
        Set a microphone/input source

        Arguments:
            device {int} -- Index of the device from {self.devices}
        """
        Logger.info(
            __name__,
            'Input source set to "%s"' % self.devices[device])

        self.selected_device = device
        self._swap_to_device = device

        values = dict(self.devices)
        values[device] = "** " + values[device]

        self.nottreal.router(
            'wizard',
            'register_option',
            label='Select microphone source',
            method=self.set_device,
            opt_type=WizardOption.DROPDOWN,
            default=False,
            values=values)

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
        if self._thread is not None:
            Logger.error(__name__, 'Already listening on another thread')
            return

        self._hot_mic = True
        self._thread = threading.Thread(target=self._listening_loop)
        self._thread.daemon = True
        self._thread.start()

    def _stop_listening(self):
        self._hot_mic = False

    def _listening_loop(self):
        Logger.info(__name__, 'Listening to the input source')

        stream = sd.InputStream(
                device=self._swap_to_device,
                callback=self._callback)
        with stream:
            self._swap_to_device = None
            while self._hot_mic \
                    and self._num_callbacks > 0 \
                    and self._swap_to_device is None:
                sd.sleep(1000)

        if self._swap_to_device is not None \
                and self._num_callbacks > 0:
            Logger.info(__name__, 'Swapping input stream')
            self._listening_loop()

        Logger.info(__name__, 'Stopped listening to the mic')
        self._thread = None

    def _callback(self, indata, frames, time, status):
        """
        Callback from sounddevice
        """
        for method in self._callbacks_volume.values():
            volume_norm = numpy.linalg.norm(indata)
            method(volume_norm)
