
import logging
import threading


class Logger:
    """
    Python logging wrapper
    from https://github.com/MixedRealityLab/conditional-voice-recorder/
    """
    _loggers = {}

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    chosen_level = logging.INFO

    COLOURS = {
        'critical': '\033[1;41m',  # red bg bold fg
        'error': '\033[1;31m',     # red bold fg
        'warning': '\033[0;43m',   # yellow bg
        'info': '\033[0m',         # no colour
        'debug': '\033[0;2m'       # grey fg
    }

    @staticmethod
    def debug(tag, message=None):
        """
        Post a debug-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('debug', tag, message)

    @staticmethod
    def info(tag, message=None):
        """Post an info-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('info', tag, message)

    @staticmethod
    def warning(tag, message=None):
        """
        Post a warning-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('warning', tag, message)

    @staticmethod
    def error(tag, message=None):
        """
        Post an error-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('error', tag, message)

    @staticmethod
    def critical(tag, message=None):
        """
        Post a critical-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('critical', tag, message)

    @staticmethod
    def log(tag, message=None):
        """
        Post a log-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('log', tag, message)

    @staticmethod
    def exception(tag, message=None):
        """
        Post an exception-level message

        Arguments:
            tag {str} -- tag for the log message
            message {str} -- log message to post
        """
        Logger._post('exception', tag, message)

    @staticmethod
    def init(level):
        """
        Initiate the logging system

        Arguments:
            level {str} -- level to set for the logger
                           (only applies on first call)
            tag {str} -- tag for the log message

        Returns:
            {Logger}
        """
        Logger.chosen_level = level
        # logging.basicConfig(
        #     format='%(asctime)s\t%(levelname)-8s\t%(name)-16s\t%(message)s',
        #     level=level)
        logging.basicConfig(
            format='%(asctime)s\t%(levelname)-4s\t%(name)-25s\t%(message)s',
            level=level)

    @staticmethod
    def _post(level, tag, message=None):
        """
        Post a message to a logger of a given tag at the given level

        Arguments:
            tag {str} -- tag for the log message
            level {str} -- level of the log message
            message {str} -- log message to post
        """
        if message is None:
            message = tag
            tag = "nottreal"

        message = "%s%s\033[0m" % (Logger.COLOURS[level], message)

        logger = Logger._get_logger(level, tag)
        method = getattr(logger, level)
        method(Logger._message(message))

    @staticmethod
    def _get_logger(level, tag):
        """
        Retrieve a Logger for a given tag

        Arguments:
            level {str} -- level to set for the logger
                           (only applies on first call)
            tag {str} -- tag for the log message

        Returns:
            {Logger}
        """
        try:
            return Logger._loggers[tag]
        except KeyError:
            trimmed_tag = tag.replace('src.nottreal', '')
            Logger._loggers[tag] = logging.getLogger(trimmed_tag)
            Logger._loggers[tag].setLevel(Logger.chosen_level)
            return Logger._loggers[tag]

    @staticmethod
    def _message(message):
        """
        Augment a message by including Thread information

        Arguments:
             message {str} -- message to post
        Returns:
            {str}
        """
        str_thread = "Thread-%d" % threading.current_thread().ident
        return "%s\t%s" % (str_thread, message)
