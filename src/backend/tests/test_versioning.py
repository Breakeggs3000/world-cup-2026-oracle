"""Tests for semver helpers."""

from __future__ import annotations

import pytest

from app.model.versioning import (
    bump_major,
    bump_minor,
    bump_patch,
    is_compatible_model_version,
    parse_semver,
)


def test_parse_and_bump():
    assert parse_semver("1.0.0") == (1, 0, 0)
    assert bump_minor("1.0.0") == "1.1.0"
    assert bump_major("1.2.3") == "2.0.0"
    assert bump_patch("1.0.0") == "1.0.1"


def test_invalid_semver():
    with pytest.raises(ValueError):
        parse_semver("not-a-version")


def test_api_model_major_compatibility():
    assert is_compatible_model_version("1.0.0", "1.2.0") is True
    assert is_compatible_model_version("1.0.0", "2.0.0") is False
