"""ANI (phone-number) normalization rules.

Uses google-libphonenumber (the `phonenumbers` package) to parse heterogeneous
phone-number strings and emit canonical E.164 representations
(`+<country><national>`, max 15 digits, no separators).
"""

import phonenumbers
from phonenumbers import NumberParseException


class AniNormalizingRules:
    @staticmethod
    def to_e164(local: str, default_region: str = "US") -> str | None:
        """Parse `local` and return its E.164 form, or None if unparseable/invalid.

        `default_region` is used when the input lacks a country-code prefix
        (e.g. bare 10-digit US/CA numbers). Anything that cannot be parsed
        or fails libphonenumber's validity check returns None so callers
        can filter it out instead of writing junk to the analytic table.
        """
        if local is None:
            return None
        local = local.strip()
        if not local:
            return None
        try:
            num = phonenumbers.parse(local, default_region)
        except NumberParseException:
            return None
        if not phonenumbers.is_valid_number(num):
            return None
        return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
