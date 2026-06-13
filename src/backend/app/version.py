"""Application and API version constants (semver)."""

from __future__ import annotations

API_VERSION = "1.0.0"
API_STATUS = "stable"  # stable | beta | deprecated

DEFAULT_MODEL_VERSION = "1.0.0"

# Bump API_VERSION on breaking response/route changes (major) or additive endpoints (minor).
