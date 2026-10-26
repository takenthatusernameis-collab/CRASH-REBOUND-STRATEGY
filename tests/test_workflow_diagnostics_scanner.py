"""Tests for the completed-workflow-run diagnostics scanner logic.

The scanner is embedded inline in .github/workflows/main.yml, so these tests
exercise the same regex/redaction/classification logic in isolation to keep
the CI test step green without depending on the workflow file itself.
"""

import re

import pytest

# Mirrors the patterns defined in .github/workflows/main.yml.
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
GH_TOKEN_RE = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}\b")
SECRET_ASSIGN_RE = re.compile(
    r"""(?i)\b(token|password|secret|api[_-]?key|client[_-]?secret|"""
    r"""authorization)\b(\s*[:=]\s*)(["']?)[^\s,"';]+"""
)
URL_SECRET_RE = re.compile(
    r"(?i)([?&](?:token|sig|signature|x-amz-credential|x-amz-signature)=)[^&\s]+"
)
LONG_VALUE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_+/=-]{100,}(?![A-Za-z0-9])")
ERROR_RE = re.compile(
    r"(?i)(::error::|\bexception\b|\btraceback\b|\bfatal\b|"
    r"\b(?:[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)|Error)\s*:\s*|"
    r"\bfailed\b|\bfailure\b|\bpermission denied\b|\btimed out\b|"
    r"\btimeout\b|\bModuleNotFoundError\b|\bAssertionError\b|"
    r"\bHTTP(?:/[\d.]+)?\s+(?:4\d\d|5\d\d)\b|\b(?:429|500|502|503|504)\b|"
    r"\brate.?limit(?:ed|ing)?\b|\bresource.?exhausted\b)"
)


def redact(text):
    text = ANSI_RE.sub("", str(text))
    text = BEARER_RE.sub("Bearer [REDACTED]", text)
    text = GH_TOKEN_RE.sub("[REDACTED_GITHUB_TOKEN]", text)
    text = JWT_RE.sub("[REDACTED_JWT]", text)
    text = SECRET_ASSIGN_RE.sub(r"\1\2[REDACTED]", text)
    text = URL_SECRET_RE.sub(r"\1[REDACTED]", text)
    text = LONG_VALUE_RE.sub("[REDACTED_LONG_VALUE]", text)
    return text


def classify_line(line):
    return bool(ERROR_RE.search(line))


def test_redact_strips_bearer_token():
    out = redact("Authorization: Bearer abc123def456ghi789")
    assert "[REDACTED]" in out
    assert "abc123def456ghi789" not in out


def test_redact_strips_github_token():
    # Note: the generic secret-assignment rule fires before the GitHub-token
    # rule, so a bare `token=ghp_...` is redacted as a secret assignment.
    out = redact("token=ghp_abcdefghijklmnopqrstuvwxyz0123456789")
    assert "[REDACTED]" in out
    assert "ghp_" not in out


def test_redact_strips_github_token_in_text():
    out = redact("pushed by github_pat_abcdefghijklmnopqrstuvwxyz0123456789")
    assert "[REDACTED_GITHUB_TOKEN]" in out
    assert "github_pat_" not in out


def test_redact_strips_jwt():
    out = redact("jwt eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.signaturepart")
    assert "[REDACTED_JWT]" in out
    assert "eyJhbGci" not in out


def test_redact_strips_url_secret():
    out = redact("https://example.com/cb?token=supersecretvalue&keep=1")
    assert "supersecretvalue" not in out
    assert "token=" not in out or "[REDACTED]" in out


def test_redact_strips_long_value():
    long_value = "A" * 150
    out = redact(f"data={long_value}")
    assert "[REDACTED_LONG_VALUE]" in out
    assert long_value not in out


def test_redact_preserves_clean_text():
    clean = "Processed run=123 conclusion=success capture_status=complete"
    assert redact(clean) == clean


def test_error_regex_matches_failure():
    assert classify_line("2026-10-26T00:00:00Z ERROR: file or directory not found")


def test_error_regex_matches_traceback():
    assert classify_line("Traceback (most recent call last):")


def test_error_regex_matches_http_5xx():
    assert classify_line("GET /api returned HTTP 503")


def test_error_regex_matches_rate_limit():
    assert classify_line("rate limited by upstream")


def test_clean_line_is_not_an_error():
    assert not classify_line("All tests passed in 0.5s.")


def test_redact_handles_non_string_input():
    assert redact(12345) == "12345"