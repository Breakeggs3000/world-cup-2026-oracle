"""Semantic versioning helpers for model artifacts."""

from __future__ import annotations

import re

_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def parse_semver(version: str) -> tuple[int, int, int]:
    match = _SEMVER_RE.match(version.strip())
    if not match:
        raise ValueError(f"Invalid semver: {version!r}")
    return int(match.group("major")), int(match.group("minor")), int(match.group("patch"))


def format_semver(major: int, minor: int, patch: int) -> str:
    return f"{major}.{minor}.{patch}"


def bump_major(version: str) -> str:
    major, _, _ = parse_semver(version)
    return format_semver(major + 1, 0, 0)


def bump_minor(version: str) -> str:
    major, minor, _ = parse_semver(version)
    return format_semver(major, minor + 1, 0)


def bump_patch(version: str) -> str:
    major, minor, patch = parse_semver(version)
    return format_semver(major, minor, patch + 1)


def is_compatible_model_version(api_version: str, model_version: str) -> bool:
    """Same major version = compatible with this API release."""
    return parse_semver(api_version)[0] == parse_semver(model_version)[0]
