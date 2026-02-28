"""E2E test configuration.

Uses DEV_MODE=true for authentication bypass, fakeredis for cache,
and SQLite in-memory database. Real JWT authentication is NOT tested
here — see test_auth_edge_cases.py for JWT-specific tests.
"""
