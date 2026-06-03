"""Username normalization rules.

Forum/site usernames come in arbitrary character sets — Unicode lookalikes,
zero-width joiners, control bytes, ligatures, full-width Latin, etc. Storing
the raw bytes lets attackers spoof identities (``Ａdmin`` vs ``Admin``) and
makes joins silently fail across visually identical but byte-different
strings (precomposed vs decomposed accents, fi-ligature vs ``fi``).

The canonical form is produced by a four-step pipeline:
  1. **NFKC normalize** — collapse compatibility characters (full-width,
     ligatures, enclosed letters, math alphanumerics, super/subscripts,
     abbreviation symbols). Recomposes decomposed accents.
  2. **Strip invisible** — remove Unicode format (``Cf``) and control
     (``Cc``) characters: zero-width joiners, BOM, directional overrides,
     ASCII controls. These are invisible attack surface with no semantic
     content in a username.
  3. **Lowercase** — case-insensitive matching.
  4. **Trim** — drop leading/trailing whitespace.

NFKC does NOT collapse confusables across scripts (Latin ``a`` vs Cyrillic
``а`` stay distinct), and the pipeline preserves internal whitespace and
punctuation so the result is still readable. SQL-injection-looking
payloads (``admin'--``, backticks, semicolons) are stored as-is — the
correct defense against SQL injection is parameterized queries at the
consumer, not ingest-time mutation.
"""

import unicodedata


class UsernameNormalizingRules:
    @staticmethod
    def nfkc(local: str) -> str:
        """Apply NFKC Unicode normalization."""
        return unicodedata.normalize("NFKC", local)

    @staticmethod
    def strip_invisible(local: str) -> str:
        """Remove Unicode format (Cf) and control (Cc) characters."""
        return "".join(
            ch for ch in local if unicodedata.category(ch) not in ("Cf", "Cc")
        )

    @staticmethod
    def make_lowercase(local: str) -> str:
        return local.lower()

    @staticmethod
    def trim(local: str) -> str:
        """Drop leading and trailing whitespace only."""
        return local.strip()

    @staticmethod
    def to_canonical(local: str) -> str | None:
        """Run the full pipeline: NFKC → strip invisible → lowercase → trim.

        Returns None for None / empty / all-invisible / whitespace-only
        inputs so the writer can drop them rather than persisting empty
        values.
        """
        if local is None:
            return None
        prepped = UsernameNormalizingRules.trim(
            UsernameNormalizingRules.make_lowercase(
                UsernameNormalizingRules.strip_invisible(
                    UsernameNormalizingRules.nfkc(local)
                )
            )
        )
        if not prepped:
            return None
        return prepped
