"""Reference implementation for python-lang-01."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from types import TracebackType
from typing import (
    ClassVar,
    Generic,
    Literal,
    Protocol,
    Self,
    TypedDict,
    TypeVar,
    overload,
    runtime_checkable,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Reader(Protocol[T_co]):
    """Read-only output makes covariance safe."""

    def get(self, index: int) -> T_co:
        """Return one value."""


@dataclass(frozen=True)
class SequenceReader(Generic[T_co]):
    values: Sequence[T_co]

    def get(self, index: int) -> T_co:
        return self.values[index]


class MutableRepository(Protocol[T]):
    """Reading and writing make the type parameter invariant."""

    def get(self, key: str) -> T | None:
        """Read a value."""

    def put(self, key: str, value: T) -> None:
        """Write a value."""


class UserCreated(TypedDict):
    kind: Literal["user_created"]
    user_id: str
    email_verified: bool


class QuotaChanged(TypedDict):
    kind: Literal["quota_changed"]
    user_id: str
    new_limit: int


DomainEvent = UserCreated | QuotaChanged


def describe_event(event: DomainEvent) -> str:
    if event["kind"] == "user_created":
        verification = "verified" if event["email_verified"] else "unverified"
        return f"user {event['user_id']} created ({verification})"
    return f"user {event['user_id']} quota -> {event['new_limit']}"


@overload
def parse_scalar(text: str, kind: Literal["int"]) -> int: ...


@overload
def parse_scalar(text: str, kind: Literal["bool"]) -> bool: ...


@overload
def parse_scalar(text: str, kind: Literal["text"]) -> str: ...


def parse_scalar(
    text: str,
    kind: Literal["int", "bool", "text"],
) -> int | bool | str:
    if kind == "int":
        return int(text)
    if kind == "bool":
        normalized = text.strip().lower()
        if normalized not in {"true", "false"}:
            raise ValueError("boolean text must be true or false")
        return normalized == "true"
    return text


class Batches(Generic[T], Iterator[tuple[T, ...]]):
    def __init__(self, items: Sequence[T], size: int) -> None:
        if size < 1:
            raise ValueError("size must be positive")
        self._items = items
        self._size = size
        self._offset = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> tuple[T, ...]:
        if self._offset >= len(self._items):
            raise StopIteration
        batch = tuple(self._items[self._offset : self._offset + self._size])
        self._offset += self._size
        return batch


class Transaction:
    """Context manager that commits a working copy only on success."""

    def __init__(self, target: list[str]) -> None:
        self._target = target
        self._working: list[str] | None = None

    def __enter__(self) -> Self:
        self._working = self._target.copy()
        return self

    def append(self, value: str) -> None:
        if self._working is None:
            raise RuntimeError("transaction is not active")
        self._working.append(value)

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if exception_type is None:
            assert self._working is not None
            self._target[:] = self._working
        self._working = None
        return False


class NonBlankText:
    """Descriptor that validates assignment and owns a private attribute name."""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self._storage_name = f"_{name}"

    @overload
    def __get__(
        self,
        instance: None,
        owner: type[object] | None = None,
    ) -> NonBlankText: ...

    @overload
    def __get__(
        self,
        instance: object,
        owner: type[object] | None = None,
    ) -> str: ...

    def __get__(
        self,
        instance: object | None,
        owner: type[object] | None = None,
    ) -> str | NonBlankText:
        if instance is None:
            return self
        value = getattr(instance, self._storage_name)
        if not isinstance(value, str):
            raise TypeError("descriptor storage was corrupted")
        return value

    def __set__(self, instance: object, value: str) -> None:
        clean = value.strip()
        if not clean:
            raise ValueError("text must not be blank")
        setattr(instance, self._storage_name, clean)


class Customer:
    name = NonBlankText()

    def __init__(self, name: str) -> None:
        self.name = name


@runtime_checkable
class Named(Protocol):
    @property
    def name(self) -> str:
        """Return a display name."""


class Labeler:
    def label(self) -> str:
        raise NotImplementedError


class Record(Labeler):
    def label(self) -> str:
        return "record"


class JsonLabelMixin(Labeler):
    def label(self) -> str:
        return f"json:{super().label()}"


class AuditedLabelMixin(Labeler):
    def label(self) -> str:
        return f"audit:{super().label()}"


class ApiRecord(JsonLabelMixin, AuditedLabelMixin, Record):
    pass


class Handler:
    """Prefer ``__init_subclass__`` over a metaclass for simple registration."""

    registry: ClassVar[dict[str, type[Handler]]] = {}
    key: ClassVar[str]

    def __init_subclass__(cls, *, key: str, **kwargs: object) -> None:
        super().__init_subclass__()
        if not key:
            raise ValueError("handler key must not be blank")
        cls.key = key
        Handler.registry[key] = cls

    def handle(self, text: str) -> str:
        raise NotImplementedError


class UpperHandler(Handler, key="upper"):
    def handle(self, text: str) -> str:
        return text.upper()


def main() -> int:
    reader: Reader[object] = SequenceReader(["alpha", "beta"])
    print("covariant reader:", reader.get(0))
    print(
        "typed event:",
        describe_event(
            UserCreated(
                kind="user_created",
                user_id="u1",
                email_verified=True,
            )
        ),
    )
    print("batches:", list(Batches([1, 2, 3, 4, 5], 2)))
    values = ["original"]
    with Transaction(values) as transaction:
        transaction.append("committed")
    print("transaction:", values)
    customer = Customer("  Ada  ")
    print("descriptor:", customer.name, isinstance(customer, Named))
    print("MRO label:", ApiRecord().label())
    print("registry:", UpperHandler().handle("local"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
