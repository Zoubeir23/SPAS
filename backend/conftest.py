"""
Project-wide pytest configuration.
"""
import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache_between_tests():
    """
    Clear the cache before every test.

    settings_test.py uses LocMemCache, which (unlike the test database) is
    not reset by Django's per-test transaction rollback. Login lockouts
    (SuspiciousActivityDetector), throttle counters, and any other
    cache-backed state would otherwise leak between test methods and even
    between unrelated TestCase classes that happen to reuse the same email
    or IP, causing spurious failures unrelated to the code under test.
    """
    cache.clear()
    yield
    cache.clear()
