import logging

class EmojiFormatter(logging.Formatter):
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥'
    }
    
    def format(self, record):
        emoji = self.EMOJI_MAP.get(record.levelname, '📝')
        record.levelname = f"{emoji}"
        return super().format(record)
