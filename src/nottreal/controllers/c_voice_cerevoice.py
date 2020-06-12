
from ..utils.log import Logger
from .c_voice import VoiceShellCmd

from subprocess import call

import time, threading, platform

class VoiceCerevoice(VoiceShellCmd):
    """
    Use the cerevoice library (not included).

    Extends:
        VoiceShellCmd
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands through to Cerevoice.
        
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
        
        self._command_speak = self._cfg.get(
            'VoiceCerevoice',
            'command_speak')
        self._command_interrupt = self._cfg.get(
            'VoiceCerevoice',
            'command_interrupt')

        self._calm_voice = False
        self._cerevoice_spurts = True
        
        self.router('wizard',
            'register_option',
            label='Calm voice',
            method=self._set_calm,
            default=self._calm_voice)
        self.router('wizard',
            'register_option',
            label='Use Cerevoice spurts?',
            method=self._set_cerevoice_spurts,
            default=self._cerevoice_spurts)

    def _set_cerevoice_spurts(self, value):
        """
        Change whether the certain shortcuts should be substituted with the 
        Cerevoice commands?
        
        Arguments:
            value {bool} -- New checked status
        """
        if value:
            Logger.debug(__name__, 'Cerevoice spurts enabled')
        else:
            Logger.debug(__name__, 'Cerevoice spurts disabled')

        self._cerevoice_spurts = value

    def _set_calm(self, value):
        """
        Change whether the words are spoken with a calm voice.
        
        Arguments:
            value {bool} -- New checked status
        """
        if value:
            Logger.debug(__name__, 'Calm voice enabled')
        else:
            Logger.debug(__name__, 'Calm voice disabled')

        self._calm_voice = value

    def _prepare_text(self, text):
        """
        Construct the command for the shell execution and prepare the text for
        display.
        
        Arguments:
            text {str} -- Text from the Wizard manager window

        Return:
            {(str, str)} -- Command and the prepared text ({None} if should not 
                be written to screen)
        """
        text_for_cmd = text.replace(' and', ', and')

        if text[-1] != '.' and text[-1] != '!' and text[-1] != '?':
            text = text + '.'

        if self._cerevoice_spurts:
            spurts = {'oh': "<spurt audio='g0001_006'>oh</spurt>", 'hm?': "<spurt audio='g0001_012'>hm?</spurt>", 'mm': "<spurt audio='g0001_015'>mm</spurt>", 'um': "<spurt audio='g0001_015'>um</spurt>", 'um?': "<spurt audio='g0001_016'>um?</spurt>", 'erm': "<spurt audio='g0001_017'>erm</spurt>", 'er': "<spurt audio='g0001_018'>er</spurt>", 'hm hm': "<spurt audio='g0001_019'>hm hm</spurt>", 'haha': "<spurt audio='g0001_020'>haha</spurt>", 'ah?': "<spurt audio='g0001_025'>ah?</spurt>", 'ah!': "<spurt audio='g0001_026'>ah!</spurt>", 'yeah?': "<spurt audio='g0001_027'>yeah?</spurt>", 'yeah': "<spurt audio='g0001_028'>yeah</spurt>", 'yeah!': "<spurt audio='g0001_029'>yeah!</spurt>", 'oh!': "<spurt audio='g0001_038'>oh</spurt>", 'hmm': "<spurt audio='g0001_039'>hmm</spurt>"} 
            try:
                text_for_cmd = spurts[text_for_cmd]
                text = None
            except KeyError:
                pass

        if self._calm_voice:
            text_for_cmd = "<usel genre='calm'>%s</usel>" % text_for_cmd

        return (self._command_speak % text_for_cmd, text)
