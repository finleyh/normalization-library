# fyc-normalize

**See a string, normalize a string.** Lightweight value normalizers for cleaning
data consistently across projects.

Each data type has one pure function that takes a single value and returns its
canonical string form, or `None` if the value is missing or unparseable. Because
the unit of work is a single value, the functions drop into pandas, polars, or
plain Python with no special integration. The only core dependency is PyYAML
(it loads the bundled email provider profiles); DataFrame and phone-parsing
support are optional extras.

## Install

```bash
pip install fyc-normalize                 # core (PyYAML only)
pip install "fyc-normalize[phone]"        # + phonenumbers, for E.164 phone parsing
pip install "fyc-normalize[domain]"       # + idna, for full IDNA2008 domain Punycode
pip install "fyc-normalize[polars]"       # + polars column helpers
pip install "fyc-normalize[pandas]"       # + pandas column helpers
```

## Usage

Every normalizer is a plain function: pass one value, get back its canonical
string form or `None`. Import what you need:

```python
from fyc_normalize import (
    normalize_email,
    normalize_ani,       # phone numbers (needs the [phone] extra)
    normalize_us_tin,    # SSN / ITIN / ATIN
    normalize_ip,
    normalize_cidr,
    normalize_domain,    # needs the [domain] extra for non-ASCII domains
    normalize_username,
)

normalize_email("Foo.Bar+promo@Gmail.com")   # "foobar@gmail.com"
normalize_ani("(415) 555-0123")              # "+14155550123"   (E.164)
normalize_us_tin("123-45-6789")              # "123456789"      (9-digit)
normalize_ip("2001:0DB8::0001")              # "2001:db8::1"    (RFC 5952)
normalize_cidr("192.168.1.5/24")             # "192.168.1.0/24" (host bits masked)
normalize_domain("WWW.Café.COM.")            # "xn--caf-dma.com" (lowercase Punycode)
normalize_username("  Ａdmin ")               # "admin"          (NFKC + lower + trim)
```

Anything missing or unparseable returns `None`, so you can filter cleanly:

```python
normalize_email("")            # None
normalize_ip("999.1.1.1")      # None
normalize_cidr("10.0.0.1")     # None  (a /prefix is required; use normalize_ip for bare addresses)
```

### Try it from the Python REPL

```console
$ uv run python
```
```python
>>> from fyc_normalize import normalize_email, normalize_domain, normalize_cidr
>>> normalize_email("  Jane.Doe+news@GMAIL.com ")
'janedoe@gmail.com'
>>> normalize_domain("_dmarc.Example.com.")
'_dmarc.example.com'
>>> normalize_cidr("2001:db8::1/64")
'2001:db8::/64'
```

Or run the bundled demo, which exercises every normalizer on messy input:

```bash
uv run python examples/demo.py
```

### In a DataFrame

Because each function takes a single value, it drops straight into pandas or polars:

```python
df["email"] = df["email"].map(normalize_email)                       # pandas
df = df.with_columns(pl.col("email").map_elements(normalize_email))  # polars
```

Or use the optional column helpers (they auto-detect polars vs pandas):

```python
from fyc_normalize.frames import normalize_email_column, normalize_ip_column
df = normalize_email_column(df, "email")     # rewrites the "email" column in place
df = normalize_ip_column(df, "client_ip")
```

> **Scope:** one job — see a string, normalize a string. Each function takes a
> single value and returns its canonical form. Nothing more.

## Design

```
src/fyc_normalize/
├── base.py          # BaseNormalizer + blank_to_none() shared pattern
├── emails.py        # EmailNormalizer + normalize_email   (profile-based)
├── anis.py          # AniNormalizer   + normalize_ani     (E.164)
├── us_tins.py       # UsTinNormalizer  + normalize_us_tin  (9-digit SSN/ITIN/ATIN)
├── ips.py           # IpNormalizer/CidrNormalizer + normalize_ip / normalize_cidr
├── domains.py       # DomainNormalizer + normalize_domain  (lowercase Punycode)
├── usernames.py     # UsernameNormalizer + normalize_username (NFKC)
├── frames.py        # optional DataFrame column helpers (lazy polars/pandas)
├── configs/         # email_profiles.yaml — provider profiles (source of truth)
└── rules/           # the actual transformation logic, one class per type
```

Each type follows the same three-part shape: a `Normalizer` class, a
module-level singleton, and a pure `normalize_*` function. The substantive
logic lives in `rules/` so behavior is easy to read, test, and change
independently of the wrappers.

### Adding a new normalizer

1. Add a rule class in `rules/<type>_rules.py`.
2. Add `<type>s.py` with a `Normalizer` subclass, singleton, and `normalize_<type>` function.
3. Export it in `__init__.py` and (optionally) add a column helper in `frames.py`.

### Email profiles

Normalization rules are selected per provider by domain, defined in
`configs/email_profiles.yaml` (loaded automatically). A provider with no domains
is the generic fallback. Each rule name must exist on `EmailNormalizingRules` and
be registered in `emails.RULE_REGISTRY`. To customize, edit the bundled YAML or
point at your own copy:

```python
from fyc_normalize.emails import EmailNormalizer
norm = EmailNormalizer(config_path="my_profiles.yaml")
norm.apply("Foo.Bar+promo@gmail.com")   # "foobar@gmail.com"
```

Currently configured providers: **gmail**, **protonmail**, **yahoo**,
**fastmail** (with its full alias-domain list), and a **generic** fallback for
everything else.

## Develop & test (uv)

This project uses [uv](https://docs.astral.sh/uv/). It manages the virtual
environment, the Python version, and dependency installation for you — there is
no venv to create or activate by hand.

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) if you
don't have it (`curl -LsSf https://astral.sh/uv/install.sh | sh` on macOS/Linux),
then from the project root:

```bash
uv sync                 # create .venv + install the package and the dev tooling
uv run pytest           # run the test suite — expect "40 passed"
```

`uv sync` installs `fyc-normalize` itself (editable) plus the `dev` dependency
group (pytest, phonenumbers, idna). `uv run` executes the command inside that
managed environment, so you never `source .../activate` yourself.

Common commands:

```bash
uv sync --all-extras            # also install polars + pandas (for the frame helpers)
uv run pytest -q                # quiet test run
uv run python examples/demo.py  # see every normalizer on sample input
uv run python                   # open a REPL with the package importable
uv pip list | grep fyc          # confirm the project installed: fyc-normalize 0.1.0 (editable)
```

> **Troubleshooting** — if `uv run pytest` reports
> `ModuleNotFoundError: No module named 'fyc_normalize'`, you almost certainly
> have an old, manually-activated virtual environment shadowing uv's. Reset it:
>
> ```bash
> deactivate            # leave any activated venv (ignore "command not found")
> rm -rf .venv          # drop the stale environment
> uv sync               # uv recreates .venv AND installs the project
> uv run pytest
> ```
>
> With uv you don't activate anything — always go through `uv run`.

(Plain `pip install -e ".[dev]"` still works if you'd rather not use uv.)

Every push and pull request runs the test suite across Python 3.10–3.13 via
GitHub Actions (`.github/workflows/ci.yml`).

## Releasing

Publishing is automated through GitHub Actions using **PyPI Trusted Publishing**
(OIDC) — no API tokens or stored secrets. **A merge to `main` publishes.** When a
pull request (e.g. `develop` → `main`) is merged, `publish.yml` builds the sdist +
wheel, runs `twine check`, and uploads to PyPI.

The workflow uses `skip-existing`, so a merge that did **not** bump the version is
a harmless no-op (the already-published version is skipped, not re-uploaded). A
new version only goes out when the version number changes.

**One-time setup** (before the first publish):

1. On PyPI, go to your account → *Publishing* → *Add a pending publisher*, and register:
   - PyPI Project Name: `fyc-normalize`
   - Owner / Repository: your GitHub org/repo
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
2. In the GitHub repo, create an environment named `pypi`
   (*Settings → Environments → New environment*). Optionally add a required
   reviewer so each publish needs approval.
3. Protect `main` (*Settings → Branches*) so changes land only via pull request.

**To ship a new version** (work on `develop`, release via PR):

1. Bump `version` in `pyproject.toml` (and `__version__` in `__init__.py`).
2. Move the `[Unreleased]` notes into a new version section in `CHANGELOG.md`.
3. Open a PR from `develop` to `main`; CI runs the test matrix on it.
4. Merge the PR. `publish.yml` runs on the resulting push to `main` and uploads
   the new version to PyPI.

To dry-run the build without publishing, trigger the workflow manually
(*Actions → Publish to PyPI → Run workflow*); the `publish` job is skipped on
manual runs. Tagging releases is optional but a nice habit (`git tag v0.1.0`).

> **Note:** normalized US TINs (SSNs, ITINs, ...) are sensitive plaintext PII.
> Treat any table that stores them as sensitive.
