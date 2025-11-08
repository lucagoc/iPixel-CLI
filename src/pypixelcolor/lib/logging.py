import logging

from .emoji_formatter import EmojiFormatter

def setup_logging(use_emojis=True):
    log_format = '%(levelname)s [%(asctime)s] [%(name)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    if use_emojis:
        formatter = EmojiFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logging.basicConfig(level=logging.INFO, handlers=[handler])