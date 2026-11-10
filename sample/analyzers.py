"""Compatibility exports for code that used the original analyzer module."""

try:
    from .lexer import DICTIONARY as dictionary, load_dictionary
except ImportError:  # Running sample/main.py directly.
    from lexer import DICTIONARY as dictionary, load_dictionary


def get_dictionary():
    return load_dictionary()
