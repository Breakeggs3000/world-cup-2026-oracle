"""Fixture provider protocol and chain."""

from __future__ import annotations

from typing import Any, Protocol


class FixtureProvider(Protocol):
    name: str

    def fetch_fixtures(self) -> list[dict[str, Any]]: ...


def run_provider_chain(providers: list[FixtureProvider]) -> tuple[list[dict[str, Any]], str]:
    last_error: str | None = None
    for provider in providers:
        try:
            fixtures = provider.fetch_fixtures()
            if fixtures:
                return fixtures, provider.name
        except Exception as exc:
            last_error = str(exc)
            continue
    if last_error:
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    return [], "none"
