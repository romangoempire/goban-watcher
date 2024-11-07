import logging


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[0;37m",  # White
        "INFO": "\033[0;36m",  # Cyan
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[0;41m",  # Red background
    }
    RESET = "\033[0m"  # Reset to default

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        formatted_msg = super().format(record)
        return f"{log_color}{formatted_msg}{self.RESET}"


# Configure the logging
format = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter(format))
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Create a logger
logger = logging.getLogger(__name__)
