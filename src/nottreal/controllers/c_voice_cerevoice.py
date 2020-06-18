
from ..utils.log import Logger
from ..models.m_mvc import WizardOption
from .c_voice import VoiceShellCmd


class VoiceCerevoice(VoiceShellCmd):
    """
    Use the cerevoice library (not included).

    Extends:
        VoiceShellCmd
    """
    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands through to Cerevoice

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

        self._opt_calm_voice = WizardOption(
                label='Use a calm voice',
                opt_cat=WizardOption.CAT_OUTPUT,
                method=self._set_calm,
                default=False,
                restorable=True)
        self.router(
            'wizard',
            'register_option',
            option=self._opt_calm_voice)

        self._opt_spurts = WizardOption(
                label='Use Cerevoice spurts',
                opt_cat=WizardOption.CAT_OUTPUT,
                method=self._set_cerevoice_spurts,
                default=True,
                restorable=True)
        self.router(
            'wizard',
            'register_option',
            option=self._opt_spurts)

    def packdown(self):
        """
        Packdown this voice subsystem (e.g. if the user changes
        the system used)
        """
        super().packdown()

        self.router(
            'wizard',
            'deregister_option',
            option=self._opt_calm_voice)

        self.router(
            'wizard',
            'deregister_option',
            option=self._opt_spurts)

    def name(self):
        return 'Cerevoice'

    def _set_cerevoice_spurts(self, value):
        """
        Change whether the certain shortcuts should be substituted with
        the Cerevoice commands?

        Arguments:
            value {bool} -- New checked status

        Return:
            {bool} -- Always {True}
        """
        Logger.info(
            __name__,
            'Set substitution of available Cerevoice spurts to %r' % value)
        return True

    def _set_calm(self, value):
        """
        Change whether the words are spoken with a calm voice

        Arguments:
            value {bool} -- New checked status

        Return:
            {bool} -- Always {True}
        """
        Logger.info(__name__, 'Set Cerevoice using a calm voice to %r' % value)
        return True

    def _prepare_text(self, text):
        """
        Construct the command for the shell execution and prepare the
        text for display

        Arguments:
            text {str} -- Text from the Wizard manager window

        Return:
            {(str, str)} -- Command and the prepared text ({None} if
                            should not be written to screen)
        """
        text_for_cmd = text.replace(' and', ', and')

        if text[-1] != '.' and text[-1] != '!' and text[-1] != '?':
            text = text + '.'

        if self._opt_spurts.value:
            spurts = {
                'oh': "<spurt audio='g0001_006'>oh</spurt>",
                'hm?': "<spurt audio='g0001_012'>hm?</spurt>",
                'mm': "<spurt audio='g0001_015'>mm</spurt>",
                'um': "<spurt audio='g0001_015'>um</spurt>",
                'um?': "<spurt audio='g0001_016'>um?</spurt>",
                'erm': "<spurt audio='g0001_017'>erm</spurt>",
                'er': "<spurt audio='g0001_018'>er</spurt>",
                'hm hm': "<spurt audio='g0001_019'>hm hm</spurt>",
                'haha': "<spurt audio='g0001_020'>haha</spurt>",
                'ah?': "<spurt audio='g0001_025'>ah?</spurt>",
                'ah!': "<spurt audio='g0001_026'>ah!</spurt>",
                'yeah?': "<spurt audio='g0001_027'>yeah?</spurt>",
                'yeah': "<spurt audio='g0001_028'>yeah</spurt>",
                'yeah!': "<spurt audio='g0001_029'>yeah!</spurt>",
                'oh!': "<spurt audio='g0001_038'>oh</spurt>",
                'hmm': "<spurt audio='g0001_039'>hmm</spurt>"}
            try:
                text_for_cmd = spurts[text_for_cmd]
                text = None
            except KeyError:
                pass

        if self._opt_calm_voice.value:
            text_for_cmd = "<usel genre='calm'>%s</usel>" % text_for_cmd

        return (self._command_speak % text_for_cmd, text)
