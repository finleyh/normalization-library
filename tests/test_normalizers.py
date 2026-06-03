import pytest

from fyc_normalize import (
    normalize_email,
    normalize_us_tin,
    normalize_username,
    normalize_ani,
    normalize_ip,
    normalize_cidr,
    normalize_domain,
)


class TestEmail:
    def test_lowercase_and_trim(self):
        assert normalize_email("  Foo@Example.COM ") == "foo@example.com"

    def test_gmail_strips_dots_and_plus_tag(self):
        assert normalize_email("Foo.Bar+promo@gmail.com") == "foobar@gmail.com"

    def test_generic_profile_keeps_dots(self):
        # non-configured domain -> generic profile: strips +tag, lowercases, trims; keeps dots
        assert normalize_email("Foo.Bar@Outlook.com") == "foo.bar@outlook.com"
        assert normalize_email("a.b.c@googlemail.com") == "a.b.c@googlemail.com"

    def test_generic_strips_plus_tag(self):
        assert normalize_email("user+news@Outlook.com") == "user@outlook.com"

    def test_subdomain_resolves_to_parent_profile(self):
        # u@sub.fastmail.com should use the fastmail profile (subdomain walk-up)
        assert normalize_email("u@mail.fastmail.com") == "u@fastmail.com"

    def test_subdomain_does_not_match_bare_tld(self):
        # an unrelated domain must fall to generic, never match a bare TLD
        assert normalize_email("Foo.Bar@notfastmail.com") == "foo.bar@notfastmail.com"

    def test_exact_match_wins_over_parent(self):
        assert normalize_email("A.B+x@gmail.com") == "ab@gmail.com"

    def test_blank_is_none(self):
        assert normalize_email("") is None
        assert normalize_email(None) is None


class TestUsTin:
    def test_strips_separators(self):
        assert normalize_us_tin("123-45-6789") == "123456789"
        assert normalize_us_tin("123 45 6789") == "123456789"

    def test_wrong_length_is_none(self):
        assert normalize_us_tin("12-345") is None
        assert normalize_us_tin("1234567890") is None

    def test_blank_is_none(self):
        assert normalize_us_tin(None) is None


class TestIp:
    def test_ipv4_strips_leading_zeros(self):
        assert normalize_ip("192.168.001.001") == "192.168.1.1"

    def test_ipv4_passthrough(self):
        assert normalize_ip("10.0.0.1") == "10.0.0.1"

    def test_ipv6_rfc5952_compression(self):
        assert normalize_ip("2001:0DB8:0000:0000:0000:0000:0000:0001") == "2001:db8::1"

    def test_ipv6_lowercased(self):
        assert normalize_ip("FE80::ABCD") == "fe80::abcd"

    def test_ipv6_brackets_stripped(self):
        assert normalize_ip("[2001:db8::1]") == "2001:db8::1"

    def test_ipv4_mapped_keeps_dotted_form(self):
        # RFC 5952 §5: embedded IPv4 stays dotted, not hex
        assert normalize_ip("::ffff:192.168.1.1") == "::ffff:192.168.1.1"

    def test_invalid_is_none(self):
        assert normalize_ip("999.1.1.1") is None
        assert normalize_ip("not.an.ip") is None
        assert normalize_ip("") is None
        assert normalize_ip(None) is None


class TestCidr:
    def test_masks_host_bits(self):
        assert normalize_cidr("192.168.1.5/24") == "192.168.1.0/24"

    def test_ipv4_passthrough(self):
        assert normalize_cidr("10.0.0.0/8") == "10.0.0.0/8"

    def test_leading_zeros(self):
        assert normalize_cidr("010.0.0.0/08") == "10.0.0.0/8"

    def test_ipv6_compressed(self):
        assert normalize_cidr("2001:0DB8::/32") == "2001:db8::/32"
        assert normalize_cidr("2001:db8::1/64") == "2001:db8::/64"

    def test_bare_address_requires_prefix(self):
        # strict: no /prefix -> None (use normalize_ip for bare addresses)
        assert normalize_cidr("192.168.1.1") is None
        assert normalize_cidr("::1") is None
        assert normalize_cidr("10.0.0.0/") is None

    def test_brackets_stripped(self):
        assert normalize_cidr("[2001:db8::]/48") == "2001:db8::/48"

    def test_invalid_is_none(self):
        assert normalize_cidr("10.0.0.0/33") is None
        assert normalize_cidr("not/a/cidr") is None
        assert normalize_cidr("") is None
        assert normalize_cidr(None) is None


class TestDomain:
    def test_lowercases_and_strips_trailing_dot(self):
        assert normalize_domain("Example.COM.") == "example.com"

    def test_strips_leading_www(self):
        assert normalize_domain("WWW.Example.com") == "example.com"

    def test_unicode_to_punycode(self):
        assert normalize_domain("café.com") == "xn--caf-dma.com"
        assert normalize_domain("MÜNCHEN.de") == "xn--mnchen-3ya.de"

    def test_already_punycode_is_stable(self):
        assert normalize_domain("xn--caf-dma.com") == "xn--caf-dma.com"

    def test_underscore_labels_allowed(self):
        assert normalize_domain("_dmarc.example.com") == "_dmarc.example.com"
        assert normalize_domain("_sip._tcp.Example.com") == "_sip._tcp.example.com"

    def test_url_like_input_is_none(self):
        assert normalize_domain("https://example.com/path") is None
        assert normalize_domain("example.com:8080") is None
        assert normalize_domain("a b.com") is None

    def test_malformed_is_none(self):
        assert normalize_domain("a..b.com") is None
        assert normalize_domain(".example.com") is None
        assert normalize_domain("") is None
        assert normalize_domain(None) is None


class TestUsername:
    def test_lowercases_and_trims(self):
        assert normalize_username("  Admin ") == "admin"

    def test_nfkc_fullwidth(self):
        # Full-width 'Ａdmin' collapses to ascii 'admin'
        assert normalize_username("Ａdmin") == "admin"

    def test_strips_zero_width(self):
        assert normalize_username("ad​min") == "admin"

    def test_all_invisible_is_none(self):
        assert normalize_username("​​") is None


# phonenumbers is an optional extra; skip cleanly if not installed.
phonenumbers = pytest.importorskip("phonenumbers")


class TestAni:
    def test_formats_us_number_to_e164(self):
        assert normalize_ani("(415) 555-0123") == "+14155550123"

    def test_respects_region(self):
        assert normalize_ani("020 7946 0958", region="GB") == "+442079460958"

    def test_garbage_is_none(self):
        assert normalize_ani("not a phone") is None

    def test_blank_is_none(self):
        assert normalize_ani("") is None
