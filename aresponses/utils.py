import re

ANY = re.compile('.*')


def _text_matches_pattern(pattern, text):
    if isinstance(pattern, str):
        if pattern == text:
            return True
    elif isinstance(pattern, re._pattern_type):
        if pattern.search(text):
            return True
    return False
