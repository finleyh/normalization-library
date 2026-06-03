# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-03

Initial release. Lightweight value normalizers with a single contract —
`normalize_x(value) -> str | None` — usable in pandas, polars, or plain Python.

### Added

- **Email** normalizer (`normalize_email`) with per-provider rule profiles
  (gmail, protonmail, yahoo, fastmail, generic) loaded from a bundled
  `email_profiles.yaml`; subdomain addresses resolve to their parent profile.
- **Phone / ANI** normalizer (`normalize_ani`) producing E.164, via the optional
  `phone` extra (`phonenumbers`).
- **US TIN** normalizer (`normalize_us_tin`) — 9-digit canonical form covering
  SSN / ITIN / ATIN (shape-only validation).
- **IP** normalizer (`normalize_ip`) for IPv4 and IPv6 (RFC 5952), including
  leading-zero handling, bracket stripping, and RFC 5952 §5 IPv4-mapped form.
- **CIDR** normalizer (`normalize_cidr`) producing `network/prefix` with host
  bits masked; a CIDR prefix is required (bare addresses return `None`).
- **Domain** normalizer (`normalize_domain`) producing lowercase Punycode via
  the optional `domain` extra (`idna`, IDNA2008), with underscore labels
  preserved and a leading `www.` stripped.
- **Username** normalizer (`normalize_username`) — NFKC, lowercased, trimmed,
  with invisible characters removed.
- Optional DataFrame column helpers in `fyc_normalize.frames` (lazy polars/pandas).
- Packaging: src-layout, zero required deps beyond PyYAML; optional extras
  `phone`, `domain`, `polars`, `pandas`, and a `dev` dependency group (PEP 735).
- uv-based developer workflow (`uv sync` / `uv run`).
- CI across Python 3.10–3.13 and PyPI publishing via Trusted Publishing (OIDC).

[Unreleased]: https://example.com/compare/v0.1.0...HEAD
[0.1.0]: https://example.com/releases/tag/v0.1.0
