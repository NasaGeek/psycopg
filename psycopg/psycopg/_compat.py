"""
compatibility functions for different Python versions
"""

# Copyright (C) 2021 The Psycopg Team

import sys
import asyncio
from typing import Any, Awaitable, Generator, Optional, Union, TypeVar

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

T = TypeVar("T")
FutureT = Union["asyncio.Future[T]", Generator[Any, None, T], Awaitable[T]]

if sys.version_info >= (3, 8):
    create_task = asyncio.create_task

else:

    def create_task(
        coro: FutureT[T], name: Optional[str] = None
    ) -> "asyncio.Future[T]":
        return asyncio.create_task(coro)


if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
    from collections import Counter, deque as Deque
else:
    from backports.zoneinfo import ZoneInfo
    from typing import Counter, Deque

__all__ = [
    "Counter",
    "Deque",
    "Protocol",
    "ZoneInfo",
    "create_task",
]
