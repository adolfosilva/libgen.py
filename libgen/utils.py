"""Utilities module.

Contains useful functions that don't belong to any class in particular.
"""

import random
import string


def random_string(length: int, character_set: str = string.ascii_lowercase) -> str:
    """Returns a random string of length 'length'
    consisting of characters from 'character_set'."""
    letters = [random.choice(character_set) for _ in range(length)]
    return "".join(letters)
