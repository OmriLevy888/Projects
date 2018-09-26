"""
        This file was originally supposed to contain all functions which could be useful anywhere
        and were not necessarily related to anywhere else in particular, but I've forgot about
        this file and just wrote them in other places so it turned out to be quite a bit shorted
        than I anticipated
"""

def is_number(s):
    """
    checks if a string is a number
    """
    try:
        x = float(s)
        return x > 0
    except ValueError:
        return False