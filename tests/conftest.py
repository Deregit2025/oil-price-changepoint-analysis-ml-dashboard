# tests/conftest.py
"""Pytest configuration and shared fixtures."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (e.g. MCMC); use -m 'not slow' to skip",
    )
