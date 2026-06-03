"""Normalization rule sets — the actual per-type transformation logic.

Each module exposes a class of @staticmethod rules. The user-facing wrappers
in the parent package call into these. Edit these files to change behavior.
"""

from .ani_rules import AniNormalizingRules
from .domain_rules import DomainNormalizingRules
from .email_rules import EmailNormalizingRules
from .ip_rules import CidrNormalizingRules, IpNormalizingRules
from .us_tin_rules import UsTinNormalizationRules
from .username_rules import UsernameNormalizingRules

__all__ = [
    "AniNormalizingRules",
    "CidrNormalizingRules",
    "DomainNormalizingRules",
    "EmailNormalizingRules",
    "IpNormalizingRules",
    "UsTinNormalizationRules",
    "UsernameNormalizingRules",
]
