"""Loss-minimising normalization used for matching, never display values."""

import re
import unicodedata

_DIACRITICS = re.compile(r"[\u064b-\u065f\u0670]")
_WHITESPACE = re.compile(r"\s+")


def normalize_fa(value: str) -> str:
    """Normalize common Arabic/Persian variants while retaining word boundaries."""
    normalized = unicodedata.normalize("NFC", value).translate(str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک", "ـ": ""}))
    normalized = _DIACRITICS.sub("", normalized).replace("\u200c", " ")
    return _WHITESPACE.sub(" ", normalized).strip()
