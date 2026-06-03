# lib/normalize/emails.py
import email

import yaml
from pathlib import Path
from meeseeks_box.utils.normalize.rules.email_rules import EmailNormalizingRules

RULE_REGISTRY = {
    'make_lowercase':         EmailNormalizingRules.make_lowercase,
    'strip_plus_as_tag':      EmailNormalizingRules.strip_plus_as_tag,
    'strip_dots':             EmailNormalizingRules.strip_dots,
    'strip_hyphen_as_tag':    EmailNormalizingRules.strip_hyphen_as_tag,
    'strip_hyphens':          EmailNormalizingRules.strip_hyphens,
    'strip_whitespace':       EmailNormalizingRules.strip_whitespace,
    'strip_underscore':       EmailNormalizingRules.strip_underscore,
    'strip_fastmail_subdomain': EmailNormalizingRules.strip_fastmail_subdomain,
    'strip_extra_at': EmailNormalizingRules.strip_extra_at,
}



class EmailNormalizingProfile:
    def __init__(self, name: str, domains: list[str], rules: list[str]):
        self.name = name
        self.domains = set(domains)
        self.rule_fns = [RULE_REGISTRY[r] for r in rules]

    def apply(self, email: str) -> str :
        for fn in self.rule_fns:
            email = fn(email)
        return email

class EmailNormalizer:
    def __init__(self, config_path: str = str(Path(__file__).parent / 'configs/email_profiles.yaml')):
        self._profiles: list[EmailNormalizingProfile] = []
        self._domain_index: dict[str, EmailNormalizingProfile] = {}
        self._generic: EmailNormalizingProfile | None = None
        self._load(config_path)

    def _load(self, config_path: str):
        with open(config_path) as f:
            config = yaml.safe_load(f)

        for name, defn in config['providers'].items():
            profile = EmailNormalizingProfile(name, defn.get('domains', []), defn['rules'])
            self._profiles.append(profile)
            if not defn.get('domains'):
                self._generic = profile
            for domain in defn.get('domains', []):
                self._domain_index[domain.lower()] = profile

    def get_profile(self, email: str) -> EmailNormalizingProfile:
        domain = email.split('@')[-1].lower() if '@' in email else ''
        profile = self._domain_index.get(domain) or self._generic
        if profile is None:
            raise ValueError("No generic fallback profile defined in email_profiles.yaml")
        return profile

    def apply(self, email: str) -> str:
        return self.get_profile(email).apply(email)


import polars as pl
# module level — instantiated once
_normalizer = EmailNormalizer()

def normalize_email_column(df: pl.DataFrame, column: str='value') -> pl.DataFrame:
    return df.with_columns(
        pl.col(column)
          .map_elements(_normalizer.apply, return_dtype=pl.Utf8)
          .alias(column)
    )