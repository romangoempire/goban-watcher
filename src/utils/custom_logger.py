import logging


# Define ANSI color codes
class LogColors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: LogColors.WHITE,
        logging.INFO: LogColors.CYAN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BOLD_RED,
    }

    def format(self, record):
        log_color = self.LEVEL_COLORS.get(record.levelno, LogColors.RESET)
        record.levelname = f"{log_color}{record.levelname}{LogColors.RESET}"
        record.msg = f"{log_color}{record.msg}{LogColors.RESET}"
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        from time import strftime

        return strftime("%Y-%m-%d %H:%M:%S", self.converter(record.created))


def get_color_logger(
    name: str = "ColorLogger", level: int = logging.DEBUG
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    logger = get_color_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
