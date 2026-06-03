"""Email normalization with per-provider rule profiles.

Each provider (gmail, fastmail, a generic fallback, ...) defines an ordered
list of rules applied to the local part / address. Profiles are selected by
the email's domain. Config can come from a YAML file (optional PyYAML extra)
or the built-in DEFAULT_PROFILES, so the package works with no dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .base import BaseNormalizer, blank_to_none
from .rules.email_rules import EmailNormalizingRules

# name -> rule function. Add a method to EmailNormalizingRules and register it here.
RULE_REGISTRY = {
    "make_lowercase": EmailNormalizingRules.make_lowercase,
    "strip_nonlegals": EmailNormalizingRules.strip_nonlegals,
    "strip_plus_as_tag": EmailNormalizingRules.strip_plus_as_tag,
    "strip_dots": EmailNormalizingRules.strip_dots,
    "strip_hyphen_as_tag": EmailNormalizingRules.strip_hyphen_as_tag,
    "strip_hyphens": EmailNormalizingRules.strip_hyphens,
    "strip_whitespace": EmailNormalizingRules.strip_whitespace,
    "strip_underscore": EmailNormalizingRules.strip_underscore,
    "strip_fastmail_subdomain": EmailNormalizingRules.strip_fastmail_subdomain,
    "strip_extra_at": EmailNormalizingRules.strip_extra_at,
}

# The provider config lives in configs/email_profiles.yaml (bundled with the
# package) and is the source of truth. A provider with no domains is the
# generic fallback. DEFAULT_PROFILES is a minimal in-code fallback used only
# if the YAML file can't be found.
DEFAULT_CONFIG_PATH = Path(__file__).parent / "configs" / "email_profiles.yaml"

DEFAULT_PROFILES = {
    "providers": {
        "generic": {
            "domains": [],  # fallback
            "rules": ["strip_extra_at", "strip_plus_as_tag", "make_lowercase", "strip_whitespace"],
        },
    }
}


class EmailNormalizingProfile:
    def __init__(self, name: str, domains: list[str], rules: list[str]):
        self.name = name
        self.domains = set(domains)
        self.rule_fns = [RULE_REGISTRY[r] for r in rules]

    def apply(self, email: str) -> str:
        for fn in self.rule_fns:
            email = fn(email)
        return email


class EmailNormalizer(BaseNormalizer):
    def __init__(self, config_path: Optional[str] = None, config: Optional[dict] = None):
        self._profiles: list[EmailNormalizingProfile] = []
        self._domain_index: dict[str, EmailNormalizingProfile] = {}
        self._generic: Optional[EmailNormalizingProfile] = None
        self._load(config or self._read_config(config_path))

    @staticmethod
    def _read_config(config_path: Optional[str]) -> dict:
        path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        if not path.exists():
            return DEFAULT_PROFILES  # resilient fallback if bundled file is missing
        import yaml  # lazy import; PyYAML is a lightweight core dependency

        with open(path) as f:
            return yaml.safe_load(f)

    def _load(self, config: dict):
        for name, defn in config["providers"].items():
            profile = EmailNormalizingProfile(name, defn.get("domains", []), defn["rules"])
            self._profiles.append(profile)
            if not defn.get("domains"):
                self._generic = profile
            for domain in defn.get("domains", []):
                self._domain_index[domain.lower()] = profile
        if self._generic is None:
            raise ValueError("No generic fallback profile defined (a provider with no domains).")

    def get_profile(self, email: str) -> EmailNormalizingProfile:
        domain = email.split("@")[-1].lower() if "@" in email else ""
        # Match the full domain first, then walk up one label at a time so a
        # subdomain resolves to its parent's profile:
        #   sub.fastmail.com -> fastmail.com  (matched)
        # We stop before the final single label so a bare TLD ("com") never
        # matches. Most-specific (longest) registered domain wins.
        labels = domain.split(".")
        for i in range(len(labels) - 1):
            profile = self._domain_index.get(".".join(labels[i:]))
            if profile is not None:
                return profile
        return self._generic

    def apply(self, value: str) -> Optional[str]:
        value = blank_to_none(value)
        if value is None:
            return None
        return self.get_profile(value).apply(value)


# module-level singleton — instantiated once with built-in defaults
_normalizer = EmailNormalizer()


def normalize_email(value: str) -> Optional[str]:
    """Normalize an email using the matching provider profile. Blank -> ``None``."""
    return _normalizer.apply(value)
