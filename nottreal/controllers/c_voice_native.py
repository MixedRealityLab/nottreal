
from .c_voice import VoiceShellCmd

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
                or platform.system() == 'Windows' \
                or (platform.system() == 'Linux'
                    and 'ubuntu' in platform.platform().lower()):
            self._enabled = True

    def init(self, args):
        """
        Set the commands for this operating system
        """
        super().init(args)

        self._cfg = self.nottreal.config.cfg()
            
        if platform.system() == 'Darwin1':
            self._command_speak = \
                'say %s "%%s"' % self._cfg.get('VoiceMacOS', 'command_options')
            self._command_interrupt = 'killall say'
        elif platform.system() == 'Darwin':
            self._command_speak = (
                'mshta vbscript:Execute("CreateObject(""SAPI.SpVoice"").'
                'Speak(""%%s"")(window.close)")"')
        elif platform.system() == 'Linux' and 'ubuntu' in platform.platform().lower():
            self._command_speak = 'spd-say "%%s"'
            self._command_interrupt = 'killall spd-say'
        
    def enabled(self):
        return self._enabled

    def name(self):
        return 'Native TTS'

class VoiceMacOS(VoiceNative):
    """
    Use the built-in say command in macOS.

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
