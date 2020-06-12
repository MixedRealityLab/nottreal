
import time, logging, threading

class Logger(object):
    """
    Python logging wrapper
    from https://github.com/MixedRealityLab/conditional-voice-recorder/
    """
    _loggers = {}

    CRITICAL=logging.CRITICAL
    ERROR=logging.ERROR
    WARNING=logging.WARNING
    INFO=logging.INFO
    DEBUG=logging.DEBUG
    NOTSET=logging.NOTSET

    chosen_level=logging.INFO

    COLOURS = {
        'critical': '\033[1;41m', # red bg bold
        'error': '\033[1;31m', # red bold
        'warning': '\033[0;43m', # yellow bg
        'info': '\033[0m', # no colour
        'debug': '\033[0;2m' # grey
    }

    @staticmethod
    def debug(tag, message=None):
        """Post a debug-level message

        Arguments:
            tag {str} -- Tag for the log message
            message {str} -- Message to post or if one is not provided, the tag
                                is used as the message instead
        """
        Logger._post('debug', tag, message)

    @staticmethod
    def info(tag, message=None):
        """Post an info-level message

        Arguments:
            tag {str} -- Tag for the log message
            message {str} -- Message to post or if one is not provided, the tag
                                is used as the message instead
        """
        Logger._post('info', tag, message)

    @staticmethod
    def warning(tag, message=None):
        """Post a warning-level message
        
        Arguments:
            tag {str} -- Tag for the log message
            message {str} -- Message to post or if one is not provided, the tag
                                is used as the message instead
        """
        Logger._post('warning', tag, message)

    @staticmethod
    def error(tag, message=None):
        """Post an error-level message

        Arguments:
            tag {str} -- Tag for the log message
            message {str} -- Message to post or if one is not provided, the tag
                                is used as the message instead
        """
        Logger._post('error', tag, message)

    @staticmethod
    def critical(tag, message=None):
        """Post a critical-level message
        
        Arguments:
            tag {str} -- Tag for the log message
            message {str} -- Message to post or if one is not provided, the tag
                                is used as the message instead
        """
        Logger._post('critical', tag, message)

    @staticmethod
    def log(tag, message=None):
        """
        Post a log-level message.

        :param String tag: tag for the log message.
        :param String message: message to post, if one is not provided, the tag
                                is used as the message instead.
        :return: None
        """
        Logger._post('log', tag, message)

    @staticmethod
    def exception(tag, message=None):
        """
        Post an exception-level message.

        :param String tag: tag for the log message.
        :param String message: message to post, if one is not provided, the tag
                                is used as the message instead.
        :return: None
        """
        Logger._post('exception', tag, message)

    @staticmethod
    def init(level):
        """
        Initiate the logging system.

        :param int level: level to set for the logger (only applies on first
                                call, can't be changed once logger is created).
        :return: Logger
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
        Post a message to a logger of a given tag at the given level.

        :param String tag: tag for the log message.
        :param String level: level of the log message, as a lowercase String,
        :param String message: message to post, the message is posted as-is, but
                        in the right colour.
        :return: None
        """
        if message == None:
            message = tag
            tag = "nottreal"

        message = "%s%s\033[0m" % (Logger.COLOURS[level], message)

        logger = Logger._get_logger(level, tag)
        method = getattr(logger, level)
        method(Logger._message(message))

    @staticmethod
    def _get_logger(level, tag):
        """
        Retrieve a Logger for a given tag.

        :param int level: level to set for the logger (only applies on first
                                call, can't be changed once logger is created).
        :param String tag: tag for the log message.
        :return: Logger
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
        Augment a message by including Thread information.

        :param String message: message to post, adds time and Thread (info)rmation
                                to the String.
        :return: String
        """
        str_thread = "Thread-%d" % threading.current_thread().ident
        return "%s\t%s" % (str_thread, message)
