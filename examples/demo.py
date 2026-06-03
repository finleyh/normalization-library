"""Quick demo of every normalizer. Run from the project root:

    uv sync
    uv run python examples/demo.py

Each row shows a messy input and its canonical normalized form (or None).
"""

from fyc_normalize import (
    normalize_ani,
    normalize_cidr,
    normalize_domain,
    normalize_email,
    normalize_ip,
    normalize_us_tin,
    normalize_username,
)

CASES = [
    ("email", normalize_email, [
        "  Foo.Bar+promo@Gmail.com ",
        "Jane-tag@yahoo.com",
        "user+news@Outlook.com",
    ]),
    ("phone (ani)", normalize_ani, [
        "(415) 555-0123",
        "+1 415-555-0123",
        "not a phone",
    ]),
    ("us_tin", normalize_us_tin, [
        "123-45-6789",
        "123 45 6789",
        "12-345",
    ]),
    ("ip", normalize_ip, [
        "192.168.001.001",
        "2001:0DB8:0000:0000:0000:0000:0000:0001",
        "[fe80::ABCD]",
    ]),
    ("cidr", normalize_cidr, [
        "192.168.1.5/24",
        "2001:db8::1/64",
        "192.168.1.1",  # no prefix -> None (strict)
    ]),
    ("domain", normalize_domain, [
        "WWW.Café.COM.",
        "_dmarc.example.com",
        "https://example.com/path",  # not a bare hostname -> None
    ]),
    ("username", normalize_username, [
        "  Admin ",
        "Ａdmin",
        "ad​min",  # zero-width space
    ]),
]


def main() -> None:
    for label, fn, inputs in CASES:
        print(f"\n## {label}")
        for raw in inputs:
            print(f"  {raw!r:45} -> {fn(raw)!r}")
    print()


if __name__ == "__main__":
    main()
