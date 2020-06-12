
from ..utils.log import Logger
from .c_voice import VoiceShellCmd

from subprocess import Popen, call

import os, time, threading

class VoiceMacOS(VoiceShellCmd):
    """
    Use the built-in say command in macOS.

    Extends:
        AbstractVoiceSystem
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to the macOS `say` command.
        
        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

    def init(self, args):
        
        """
        Set the macOS commands.
        """
        super().init(args)
        
        self._cfg = self.nottreal.config.cfg()
        
        self._command_speak = \
            'say %s "%%s"' % self._cfg.get('VoiceMacOS', 'command_options')
        self._command_interrupt = 'killall say'
