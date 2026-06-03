"""Shared base pattern for all normalizers.

Every normalizer follows the same shape, mirroring the uploaded examples:

    class FooNormalizer(BaseNormalizer):
        def apply(self, value: str) -> str | None: ...

    _normalizer = FooNormalizer()          # module-level singleton
    normalize_foo = _normalizer.apply       # pure, lambda-friendly function

The core contract is deliberately tiny: a normalizer takes one value and
returns its canonical string form, or ``None`` if the value is missing or
unparseable. Because the unit of work is a single value, these functions
drop straight into any pipeline:

    pandas:  df["email"] = df["email"].map(normalize_email)
    polars:  df.with_columns(pl.col("email").map_elements(normalize_email))
    python:  normalize_email(raw)
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class Normalizer(Protocol):
    """Structural type for anything that normalizes a single value."""

    def apply(self, value: str) -> Optional[str]: ...


class BaseNormalizer:
    """Convenience base that makes instances directly callable.

    Subclasses implement ``apply``; calling the instance delegates to it,
    so a singleton doubles as a plain function.
    """

    def apply(self, value: str) -> Optional[str]:  # pragma: no cover - abstract
        raise NotImplementedError

    def __call__(self, value: str) -> Optional[str]:
        return self.apply(value)


def blank_to_none(value: Optional[str]) -> Optional[str]:
    """Return ``None`` for missing/blank input, else the stripped string.

    Used at the top of every ``apply`` so normalizers never have to repeat
    null-handling boilerplate.
    """
    if value is None:
        return None
    text = str(value).strip()
    return text or None
