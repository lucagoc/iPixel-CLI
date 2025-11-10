from logging import getLogger
logger = getLogger(__name__)

# Utility functions

def validate_range(value, min_val, max_val, name):
    """Validate that a value is within a specific range."""
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}")
