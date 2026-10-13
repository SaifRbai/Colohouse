from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

_handlers: dict[type, list[Callable]] = defaultdict(list)


def subscribe(event_type: type):
    def decorator(fn: Callable):
        _handlers[event_type].append(fn)
        return fn
    return decorator


def emit(event) -> None:
    for handler in _handlers[type(event)]:
        handler(event)


@dataclass(frozen=True)
class HousingRequestAccepted:
    request_id: int
    host_id: int
    seeker_id: int
    conversation_id: int


@dataclass(frozen=True)
class HousingRequestCreated:
    request_id: int
    host_id: int
    seeker_id: int
