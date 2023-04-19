"""
utils.py

Utils functions.
"""

import os

import discord

# Number of milliseconds in an hour
NB_MILLISECONDS_PER_HOUR = 3600000

# Maximum number of options a Discord autocomplete view can display
DISCORD_AUTOCOMPLETE_CHOICES_LIMIT = 25

# Maximum length of a Discord embed title
DISCORD_EMBED_TITLE_MAX_LEN = 256

# Maximum length of a Discord embed description
DISCORD_EMBED_DESCRIPTION_MAX_LEN = 4096

# Maximum length of a Discord embed field value
DISCORD_EMBED_FIELD_VALUE_MAX_LEN = 1024

def truncate_text(text: str, size: int) -> str:
    """Truncates a text to size bytes.

    Args:
        text (str):
            The text to truncate.
        size (int):
            The maximum size.

    Returns:
        The text truncated.
    """
    return (text[:size - 3] + '...') if len(text) > size else text

def upload_image(path: str) -> tuple:
    """Uploads a local image to the Discord API.

    Args:
        path (str):
            The path to the local image

    Returns:
        A tuple containing the url attachment and the Discord file.
    """
    return (f'attachment://{os.path.basename(path)}', discord.File(path))
