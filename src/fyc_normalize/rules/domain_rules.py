"""Domain / hostname normalization rules.

Canonical form is the lowercase **Punycode (ASCII A-label)** representation:

  * ``WWW.Example.COM.``        -> ``example.com``
  * ``café.com``               -> ``xn--caf-dma.com``
  * ``MÜNCHEN.de``             -> ``xn--mnchen-3ya.de``

Rationale: the A-label form is DNS-native, unambiguous, and join-safe — two
visually identical Unicode spellings collapse to the same ASCII key.

Behavior:
  * Internationalized (non-ASCII) labels are converted to Punycode via the
    ``idna`` package (IDNA2008 / UTS-46) when installed, falling back to the
    stdlib ``idna`` codec (IDNA2003). Install the ``domain`` extra for full
    IDNA2008: ``pip install "fyc-normalize[domain]"``.
  * Underscore labels are preserved (``_dmarc.example.com``, ``_sip._tcp...``)
    — common in DNS TXT/SRV records and not valid IDNA, so ASCII labels are
    passed through (lowercased) rather than IDNA-encoded.
  * A single trailing dot (FQDN root) is stripped.
  * A leading ``www.`` label is stripped.
  * Bare hostnames only: input containing a scheme, path, port, userinfo, or
    whitespace (anything URL-like) returns ``None``.

Anything that isn't a valid hostname after this returns ``None``.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

try:  # optional: full IDNA2008 / UTS-46
    import idna as _idna
except ImportError:  # pragma: no cover - exercised only without the extra
    _idna = None

# Reject URL-ish / whitespace characters so only bare hostnames pass.
_INVALID_CHARS = frozenset(" \t\r\n/\\?#@:")

# An already-ASCII label: letters, digits, hyphen, underscore.
_ASCII_LABEL = re.compile(r"^[a-z0-9_-]+$")


def _to_alabel(label: str) -> Optional[str]:
    """Convert a non-ASCII label to its Punycode A-label, or ``None``."""
    if _idna is not None:
        try:
            return _idna.encode(label, uts46=True, transitional=False).decode("ascii")
        except Exception:
            return None
    try:  # stdlib fallback (IDNA2003)
        return label.encode("idna").decode("ascii")
    except Exception:
        return None


class DomainNormalizingRules:
    @staticmethod
    def to_canonical(value: str) -> Optional[str]:
        """Return the canonical lowercase Punycode domain, or ``None``."""
        if value is None:
            return None
        text = unicodedata.normalize("NFC", str(value).strip())
        if not text or any(ch in _INVALID_CHARS for ch in text):
            return None

        # Strip a single trailing dot (the FQDN root label).
        if text.endswith("."):
            text = text[:-1]
        if not text:
            return None

        labels: list[str] = []
        for label in text.split("."):
            if label == "":
                return None  # empty label: leading or consecutive dots
            if label.isascii():
                label = label.lower()
                if not _ASCII_LABEL.match(label):
                    return None
            else:
                label = _to_alabel(label)
                if label is None:
                    return None
            labels.append(label)

        # Strip a leading "www." (but never reduce to nothing).
        if len(labels) > 1 and labels[0] == "www":
            labels = labels[1:]

        # DNS length limits on the A-label form: 1-63 octets per label, <=253 total.
        if not labels or any(not 1 <= len(lbl) <= 63 for lbl in labels):
            return None
        result = ".".join(labels)
        if len(result) > 253:
            return None
        return result
