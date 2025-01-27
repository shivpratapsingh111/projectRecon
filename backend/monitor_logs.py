import logging
import requests

# Your existing function to send telegram messages
def send_telegram_message(message: str):
    url = 
    payload = {
        ,
        'text': message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        logger.info("Message sent successfully")
    else:
        logger.exception(f"Failed to send message: {response.status_code}")

# Custom logging handler to send telegram messages on error
class TelegramErrorHandler(logging.Handler):
    def emit(self, record):
        try:
            if record.levelno >= logging.ERROR:
                message = self.format(record)
                send_telegram_message(message)
        except Exception as e:
            logger.exception(f"Error in TelegramErrorHandler: {e}")

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Capture all logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Add the custom handler to the logger
telegram_handler = TelegramErrorHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
telegram_handler.setFormatter(formatter)
logger.addHandler(telegram_handler)

# Test the logging
try:
    1 / 0  # This will raise a ZeroDivisionError
except ZeroDivisionError as e:
    logger.error(f"An error occurred: {e}")
