"""Day 2 reference: small Protocols, resource contexts, and typed decorators."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import wraps
from typing import ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class Connection(Protocol):
    """The behavior needed by the transaction context—not a concrete driver class."""

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class ConnectionFactory(Protocol):
    """A callable that opens one connection."""

    def __call__(self) -> Connection: ...


@contextmanager
def managed_connection(factory: ConnectionFactory) -> Iterator[Connection]:
    """Commit on success, roll back on failure, and always close."""

    connection = factory()
    try:
        yield connection
    except BaseException:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


def logged(
    function: Callable[P, R],
    *,
    logger: logging.Logger | None = None,
) -> Callable[P, R]:
    """Log call outcome while preserving the wrapped function's signature."""

    selected_logger = logger or logging.getLogger(function.__module__)

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        selected_logger.debug("starting function=%s", function.__qualname__)
        try:
            result = function(*args, **kwargs)
        except BaseException:
            selected_logger.exception("failed function=%s", function.__qualname__)
            raise
        selected_logger.debug("finished function=%s", function.__qualname__)
        return result

    return wrapper


@logged
def normalize_customer_name(name: str) -> str:
    """A small function used to demonstrate signature-preserving decoration."""

    normalized = " ".join(name.split())
    if not normalized:
        raise ValueError("customer name cannot be blank")
    return normalized.title()
