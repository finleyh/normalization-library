"""IP-address normalization rules (IPv4 and IPv6).

Canonical form uses Python's stdlib ``ipaddress`` (no dependency):

  * IPv4 -> dotted-decimal with leading zeros stripped: ``192.168.001.001``
    becomes ``192.168.1.1``.
  * IPv6 -> RFC 5952 canonical form: lowercase hex, leading zeros dropped per
    group, and the longest run of zero groups compressed to ``::``. So
    ``2001:0DB8:0000:0000:0000:0000:0000:0001`` becomes ``2001:db8::1``.

Convenience handling for messy real-world data:
  * Surrounding brackets on IPv6 literals (``[2001:db8::1]``, as used in URLs)
    are stripped before parsing.
  * Leading-zero IPv4 octets are treated as decimal. Modern ``ipaddress``
    rejects ``010`` as ambiguous-octal; we normalize it to ``10`` instead of
    dropping the row.

Anything that is not a valid IP after this returns ``None`` so callers can
filter it out. IPv6 scope/zone IDs (``fe80::1%eth0``) are preserved.
"""

from __future__ import annotations

import ipaddress
import re
from typing import Optional

# Four 1-3 digit groups separated by dots — an IPv4-shaped string.
_DOTTED_IPV4 = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


class IpNormalizingRules:
    @staticmethod
    def to_canonical(value: str) -> Optional[str]:
        """Return the canonical IPv4/IPv6 string, or ``None`` if invalid."""
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None

        # Strip brackets around an IPv6 literal, e.g. "[2001:db8::1]".
        if len(text) >= 2 and text[0] == "[" and text[-1] == "]":
            text = text[1:-1].strip()

        # Decimal IPv4 with leading zeros: parse octets as base-10 and rebuild
        # so "192.168.001.001" -> "192.168.1.1" rather than erroring out.
        if _DOTTED_IPV4.match(text):
            text = ".".join(str(int(octet)) for octet in text.split("."))

        try:
            ip = ipaddress.ip_address(text)
        except ValueError:
            return None

        # RFC 5952 §5: IPv4-mapped IPv6 keeps the embedded IPv4 in dotted form
        # (Python's default str() would render it as hex, e.g. ::ffff:c0a8:101).
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            return f"::ffff:{ip.ipv4_mapped}"
        return str(ip)


class CidrNormalizingRules:
    """Normalize CIDR / network notation (IPv4 and IPv6).

    Canonical form is ``network/prefix`` with host bits masked off and the
    address rendered like ``IpNormalizingRules`` (dotted IPv4, RFC 5952 IPv6):

      * ``192.168.1.5/24``   -> ``192.168.1.0/24``   (host bits zeroed)
      * ``2001:0DB8::/32``   -> ``2001:db8::/32``

    A CIDR prefix is required: a bare address with no ``/prefix`` returns
    ``None`` (use ``IpNormalizingRules`` for bare addresses). Leading-zero IPv4
    octets are normalized and surrounding brackets on an IPv6 literal are
    stripped, as in ``IpNormalizingRules``. Invalid -> ``None``.
    """

    @staticmethod
    def to_canonical(value: str) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None

        addr, sep, prefix = text.rpartition("/")
        if not sep or prefix == "":  # strict: a CIDR prefix is required
            return None

        # Strip brackets around an IPv6 literal, e.g. "[2001:db8::]/48".
        if len(addr) >= 2 and addr[0] == "[" and addr[-1] == "]":
            addr = addr[1:-1].strip()

        # Decimal IPv4 with leading zeros -> base-10 octets (see IpNormalizingRules).
        if _DOTTED_IPV4.match(addr):
            addr = ".".join(str(int(octet)) for octet in addr.split("."))

        candidate = addr if prefix == "" else f"{addr}/{prefix}"
        try:
            # strict=False masks host bits to the network address instead of erroring.
            net = ipaddress.ip_network(candidate, strict=False)
        except ValueError:
            return None
        return str(net)
