import logging


class ColoredFormatter(logging.Formatter):
    """
    A custom formatter class that adds color to log messages.
    """

    COLOR_CODES = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[1;41m',  # White on red background
    }

    def format(self, record):
        """
        Format the log message with color.

        :param record: The log record to format.
        :type record: LogRecord
        :return: The formatted log message with color.
        :rtype: str
        """
        log_message = super().format(record)
        return f"{self.COLOR_CODES[record.levelname]}{log_message}\033[0m"


def setup_logging(level="INFO"):
    """
    Set up colored logging.

    This function configures colored logging using the ColoredFormatter class.

    :param level: The logging level.
    :type level: str
    :return: The configured logger instance.
    :rtype: Logger
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

    # Default to INFO level if the provided level is not valid
    level_to_set = level_map.get(level, "INFO")

    # Init logger
    logger = logging.getLogger()
    logger.setLevel(level_to_set)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add a new handler
    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Log incorrect level parameter
    if level not in level_map:
        logger.warning(f"Invalid logging level '{level}' provided. Defaulting to 'INFO'.")

    return logger

# Initialize the logger
logger = setup_logging(level="INFO")
