from datetime import datetime


def get_current_date_info() -> str:
    """Get current date information in a detailed format."""
    now = datetime.now()

    # Format: Saturday, March 2, 2025
    date_str = now.strftime("%A, %B %d, %Y")

    return date_str
