"""Bind a certificate to its declared instance by deterministic recomputation.

Many certificates in this package store both an instance (a graph, a prior, a
channel, a horizon, enumeration caps) and the solution data that the exact
solver produced for it. Checking only the internal arithmetic of the solution
data is not enough: a hand-built certificate can be internally consistent and
still describe the wrong instance, drop constraints, or report a non-optimal
value. ``matches_rebuild`` closes that gap. It reruns the deterministic exact
builder on the instance stored in the certificate and requires the result to be
equal, field by field, to the certificate being validated.

While a reference certificate is being rebuilt, nested ``valid`` calls skip
their own rebuild (they still run their arithmetic checks); the outer equality
test then covers the nested data as well. Successful and failed checks are
cached by object identity, so repeated ``valid`` calls on one object rebuild
once.
"""

from __future__ import annotations

from typing import Any, Callable

_ACTIVE = 0
_CACHE: dict[int, tuple[Any, bool]] = {}
_CACHE_LIMIT = 4096

_BUILD_ERRORS = (
    ValueError,
    ArithmeticError,
    AssertionError,
    KeyError,
    IndexError,
    TypeError,
    AttributeError,
    RecursionError,
)


def rebuilding() -> bool:
    """True while a reference certificate is being rebuilt."""

    return _ACTIVE > 0


def matches_rebuild(certificate: Any, build: Callable[[], Any]) -> bool:
    """Return whether ``build()`` reproduces ``certificate`` exactly."""

    global _ACTIVE
    if _ACTIVE:
        return True
    key = id(certificate)
    cached = _CACHE.get(key)
    if cached is not None and cached[0] is certificate:
        return cached[1]
    _ACTIVE += 1
    try:
        reference = build()
        result = reference == certificate
    except _BUILD_ERRORS:
        result = False
    finally:
        _ACTIVE -= 1
    if len(_CACHE) >= _CACHE_LIMIT:
        _CACHE.clear()
    _CACHE[key] = (certificate, result)
    return result
