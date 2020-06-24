
from ..utils.log import Logger
from ..models.m_mvc import VUIState, WizardAlert
from .c_voice import NonBlockingThreadedBaseVoice

from collections import deque

import importlib


class VoiceActiveMQ(NonBlockingThreadedBaseVoice):
    """
    Send the voice to an ActiveMQ/STOMP channel and create a channel
    for receiving  messages back. Configuration is in the main
    settings.cfg file.

    This uses stomp.py, which you can install with pip:
        pip3 install stomp.py

    Simply put, this controller will send messages to be spoken now
    to an ActiveMQ/STOMP channel, and assume they are spoken
    immediately and are  currently being spoken until there is a
    message sent back.

    We assume that when we send a message, it is spoken immediately.
    That said, we listen back from whatever is at the other end for
    speaking and nothing states, and change/update our state when
    `speaking` is happening. This allows for a remote system to
    block new messages.

    Extends:
        NonBlockingThreadedBaseVoice

    Variables:
        RECEIVE_QUEUE, SEND_QUEUE {int} -- ActiveMQ queue identifiers

    Extends:
        AbstractVoiceSystem
    """
    RECEIVE_QUEUE, SEND_QUEUE = range(0, 2)

    def __init__(self, nottreal, args):
        """
        Create the thread that sends commands to an ActiveMQ/STOMP
        queue

        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        super().__init__(nottreal, args)

    def init(self, args):
        """
        Load the configuration and connect to the ActiveMQ/STOMP
        server, and register the NottReal receiver
        """
        super().init(args)

        Logger.debug(__name__, 'Loading "stomp" module')
        self.stomp = importlib.import_module('stomp')

        self._cfg = self.nottreal.config.cfg()

        self._queued_messages = deque()

        self._host = self._cfg.get('ActiveMQ', 'host')
        self._port = self._cfg.getint('ActiveMQ', 'port')
        self._username = self._cfg.get('ActiveMQ', 'username')
        self._password = self._cfg.get('ActiveMQ', 'password')
        self._receive_queue = self._cfg.get('ActiveMQ', 'nottreal_queue')
        self._send_queue = self._cfg.get('ActiveMQ', 'destination_queue')

        self._message = self._cfg.get('ActiveMQ', 'message_text')
        self._message_interrupt = self._cfg.get(
            'ActiveMQ',
            'message_interrupt')

        Logger.debug(
            __name__,
            'Connecting to ActiveMQ server %s:%d' % (self._host, self._port))

        try:
            self._conn = self.stomp.Connection([(self._host, self._port)])
            self._conn.set_listener('', VoiceActiveMQ.Listener(self))
            self._conn.connect(self._username, self._password, wait=True)

            Logger.debug(__name__, 'Subscribing to %s' % self._receive_queue)
            self._conn.subscribe(
                destination=self._receive_queue,
                id=self.RECEIVE_QUEUE,
                ack='auto')
        except self.stomp.exception.ConnectFailedException:
            self._conn = False
            Logger.critical(
                __name__,
                'Failed to connect to ActiveMQ/STOMP server')

            self._alert_not_connected()

    def _alert_not_connected(self):
        """
        Show the Wizard that we aren't connected to an
        ActiveMQ server
        """
        alert = WizardAlert(
            'ActiveMQ/STOMP Connection Error',
            ('Could not connect to the ActiveMQ/STOMP server "%s:%s".\n\n'
                + 'Ensure ActiveMQ/STOMP is running and try again.')
            % (self._host, self._port),
            WizardAlert.LEVEL_ERROR)

        self.router('wizard', 'show_alert', alert=alert)

    def packdown(self):
        """
        Packdown this voice subsystem (e.g. if the user changes
        the system used)
        """
        super().packdown()

        if self._conn:
            self._conn.disconnect()

    def name(self):
        return 'ActiveMQ'

    class Listener():
        """
        Listen to messages from the ActiveMQ/STOMP server

        Extends:
            stomp.ConnectionListener

        Arguments:
            app {App} -- Application instance
        """
        def __init__(self, parent):
            self.parent = parent
            self.nottreal = parent.nottreal
            self._cfg = self.nottreal.config.cfg()

            message_state_format = self._cfg.get('ActiveMQ', 'message_state')
            self._message_state_nothing = \
                message_state_format \
                % self._cfg.get('ActiveMQ', 'message_state_nothing')
            self._message_state_speaking = \
                message_state_format \
                % self._cfg.get('ActiveMQ', 'message_state_speaking')
            self._message_state_listening = \
                message_state_format \
                % self._cfg.get('ActiveMQ', 'message_state_listening')
            self._message_state_computing = \
                message_state_format \
                % self._cfg.get('ActiveMQ', 'message_state_computing')

        def on_error(self, headers, message):
            Logger.error(
                __name__,
                'Error passed via ActiveMQ/STOMP: %s' % message)

        def on_message(self, headers, message):
            if message == self._message_state_nothing:
                Logger.debug(__name__, 'Apparently nothing is happening....')
                self.parent._on_stop_speaking(state=VUIState.RESTING)

            elif message == self._message_state_listening:
                Logger.debug(__name__, 'Apparently we\'re listening...')
                self.parent._on_stop_speaking(state=VUIState.LISTENING)

            elif message == self._message_state_computing:
                Logger.debug(
                    __name__,
                    'Apparently computation is happening...')
                self.parent._on_stop_speaking(state=VUIState.BUSY)

            elif message == self._message_state_speaking:
                try:
                    self.parent._on_start_speaking(
                        self.parent._queued_messages.pop())
                    Logger.debug(__name__, 'Apparently we\'re speaking...')
                except IndexError:
                    Logger.error(
                        __name__,
                        'Apparently we\'re speaking, but we don\' know what')

            else:
                Logger.warning(__name__, 'Unknown message: %s' % message)

    def _prepare_text(self, text):
        """
        Construct the command for the shell execution and prepare
        the text for display

        Arguments:
            text {str} -- Text from the Wizard manager window

        Return:
            {(str, str)} -- Command and the prepared text ({None} if
                should not be written to screen)
        """
        if not self._conn:
            Logger.critical(__name__, 'Not connected to ActiveMQ/STOMP server')
            return ('', '')

        return (self._message % text, text)

    def _produce_voice(self,
                       text,
                       prepared_text,
                       cat=None,
                       id=None,
                       slots=None):
        """
        Receive the text (which should be a command), and then call it

        Arguments:
            text {str} -- Text to record as being produced
            prepared_text {str} -- Command to call through a shell

        Keyword Arguments:
            cat {str} -- Category ID if a prepared message
            id {str} -- Prepared message ID if a prepared message
            slots {dict(str,str)} -- Slots changed by the user
        """
        if not self._conn:
            Logger.critical(__name__, 'Not connected to ActiveMQ/STOMP server')
            return

        Logger.debug(__name__, 'Sending message: %s' % prepared_text)
        self.send_to_recorder(text, cat, id, slots)
        self._queued_messages.append(text)
        self._conn.send(body=prepared_text, destination=self._send_queue)

    def _interrupt_voice(self):
        """
        Immediately cancel waiting (if we are waiting)
        """
        if not self._conn:
            Logger.critical(__name__, 'Not connected to ActiveMQ/STOMP server')
            return

        self._conn.send(
            body=self._message_interrupt,
            destination=self._send_queue)
