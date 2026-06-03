"""fyc_normalize — lightweight, dependency-free value normalizers.

Public API: one pure function per data type. Each takes a single value and
returns its canonical string form, or ``None`` if missing/unparseable. Drop
them into pandas, polars, or plain Python:

    from fyc_normalize import normalize_email, normalize_ani, normalize_us_tin, normalize_username

    normalize_email("Foo.Bar+promo@Gmail.com")   # -> "foobar@gmail.com"
    normalize_ani("(415) 555-0123")                # -> "+14155550123"  (needs `phone` extra)
    normalize_us_tin("123-45-6789")                   # -> "123456789"
    normalize_ip("2001:0DB8::0001")                # -> "2001:db8::1"
    normalize_cidr("192.168.1.5/24")               # -> "192.168.1.0/24"
    normalize_domain("WWW.Café.COM.")              # -> "xn--caf-dma.com"
    normalize_username("  Ａdmin​ ")           # -> "admin"

    # pandas:  df["email"] = df["email"].map(normalize_email)
    # polars:  df.with_columns(pl.col("email").map_elements(normalize_email))

Optional DataFrame column helpers live in ``fyc_normalize.frames``.
The transformation classes/singletons are also exported for advanced use.
"""

from .anis import AniNormalizer, normalize_ani
from .domains import DomainNormalizer, normalize_domain
from .emails import EmailNormalizer, normalize_email
from .ips import CidrNormalizer, IpNormalizer, normalize_cidr, normalize_ip
from .us_tins import UsTinNormalizer, normalize_us_tin
from .usernames import UsernameNormalizer, normalize_username

__all__ = [
    "normalize_email",
    "normalize_ani",
    "normalize_domain",
    "normalize_ip",
    "normalize_cidr",
    "normalize_us_tin",
    "normalize_username",
    "EmailNormalizer",
    "AniNormalizer",
    "DomainNormalizer",
    "IpNormalizer",
    "CidrNormalizer",
    "UsTinNormalizer",
    "UsernameNormalizer",
]

__version__ = "0.1.0"
