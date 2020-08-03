
from ..utils.log import Logger
from .c_voice import ThreadedBaseVoice, VoiceShellCmd

import importlib
import platform


class VoiceNative(VoiceShellCmd):
    """
    Use the built-in operating system voice

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to native voice.

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)
        self._enabled = False

        if platform.system() == 'Darwin' \
                or (platform.system() == 'Linux'
                    and 'ubuntu' in platform.platform().lower()):
            self._enabled = True

    def init(self, args):
        """
        Set the commands for this operating system
        """
        super().init(args)

        self._cfg = self.nottreal.config.cfg()

        if platform.system() == 'Darwin':
            self._command_speak = \
                'say %s "%%s"' % self._cfg.get('VoiceMacOS', 'command_options')
            self._command_interrupt = 'killall say'
        elif platform.system() == 'Linux' \
                and 'ubuntu' in platform.platform().lower():
            self._command_speak = 'spd-say "%%s"'
            self._command_interrupt = 'killall spd-say'

    def enabled(self):
        return self._enabled

    def name(self):
        return 'Native TTS'


class VoiceMacOS(VoiceNative):
    """
    Use the built-in say command in macOS. Here for legacy
    reasons only.

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to the macOS `say`
        command

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)


class VoiceWindows(ThreadedBaseVoice):
    """
    Use the built-in SAPI TTS on Windows.

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to SAPI

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

        self._enabled = False

        if platform.system() == 'Windows':
            try:
                Logger.debug(__name__, 'Loading "win32com" module')
                self.win32com = \
                    importlib.import_module('win32com.client')
                self._enabled = True
            except ModuleNotFoundError:
                Logger.warning(
                    __name__,
                    '"win32com" module not installed - ' +
                    'disabling Native TTS on Windows')
                pass

    def init(self, args):
        """
        Load the configuration.
        """
        super().init(args)

        if not self.enabled():
            return

        self._speaker = self.win32com.Dispatch('SAPI.SpVoice')

    def enabled(self):
        return self._enabled

    def name(self):
        return 'Native TTS'

    def _produce_voice(self,
                       text,
                       prepared_cmd,
                       cat=None,
                       id=None,
                       slots=None):
        """
        Receive the text (which should be a command), and then
        call it.

        Arguments:
            text {str} -- Text to record as being produced
            prepared_cmd {str} -- Command to call through a shell

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        if not self.enabled():
            return

        self.send_to_recorder(text, cat, id, slots)
        Logger.debug(__name__, 'Speaking %s' % prepared_cmd)

        self._speaker.Speak(prepared_cmd)
        self._speaker.SpeakCompleteEvent()

    def _interrupt_voice(self):
        """
        Immediately cancel waiting (if we are waiting)
        """
        if not self.enabled():
            return

        Logger.error('voice', 'Interrupt not supported with Windows')
