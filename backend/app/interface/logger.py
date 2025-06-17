# External Imports
import threading, requests, logging, os

# Internal imports
from app.config.config import LOGS_DIR, TELEGRAM_WEBHOOK, TELEGRAM_CHAT_ID

# Initialization

# Your existing function to send telegram messages
def send_telegram_message(message: str):
    url = TELEGRAM_WEBHOOK
    payload = {
        'chat_id': f'{TELEGRAM_CHAT_ID}',
        'text': message
    }


    try:
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send Telegram message. [Maybe No Internet]")

# Custom logging handler to send telegram messages on error
class TelegramErrorHandler(logging.Handler):
    def emit(self, record):
        try:
            if record.levelno >= logging.ERROR:
                message = self.format(record)
                threading.Thread(target=send_telegram_message, args=(message,), daemon=True).start()
        except Exception as e:
            print(f"Error in TelegramErrorHandler: {e}")

def setup_logger(name, log_file_path, enable_debug: bool = False):
    # Create the logger instance
    logger = logging.getLogger(name)

    os.makedirs(LOGS_DIR, exist_ok=True)
    
    log_level = logging.DEBUG if enable_debug else logging.INFO
    logger.setLevel(log_level)

    logger.propagate = False
    
    # Prevent duplicate log entrieslog.log
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(f"{LOGS_DIR}/{log_file_path}.log", mode='a')
        console_handler = logging.StreamHandler()
        
        # Create formatter and set it for both handlers
        log_format = '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s'
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add both handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Add the TelegramErrorHandler to handle errors and send notifications
        telegram_handler = TelegramErrorHandler()
        telegram_handler.setFormatter(formatter)
        logger.addHandler(telegram_handler)

    return logger
