from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import inspect
from collections import OrderedDict
from collections.abc import Callable, Coroutine, Hashable
from functools import _CacheInfo, _make_key, partial, partialmethod  # pyright: ignore[reportPrivateUsage]
from typing import (
    Any,
    Concatenate,
    Generic,
    TypedDict,
    TypeVar,
    cast,
    final,
    overload,
)

from typing_extensions import ParamSpec, Self

__all__ = (
    "alru_cache",
    "parse_rpn_expression",
)


_BINARY_OPS: frozenset[str] = frozenset(
    {
        "+",
        "-",
        "*",
        "/",
        "%",
        ">>",
        "<<",
        "&",
        "|",
        "^",
        "==",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "&&",
        "||",
        "and",
        "or",
    }
)
_COMPARISON_OPS: frozenset[str] = frozenset({"==", "!=", "<", ">", "<=", ">="})
_LOGICAL_OPS: frozenset[str] = frozenset({"&&", "||", "and", "or"})
_UNARY_OPS: frozenset[str] = frozenset({"!", "not", "~"})

_P = ParamSpec("_P")
_P2 = ParamSpec("_P2")
_T = TypeVar("_T", bound=Hashable)
_R = TypeVar("_R")
_Coro = Coroutine[Any, Any, _R]
_CB = Callable[_P, _Coro[_R]]
_CBP = _CB[_P, _R] | partial[_Coro[_R]] | partialmethod[_Coro[_R]]


@final
class _CacheParameters(TypedDict):
    typed: bool
    maxsize: int | None
    tasks: int
    closed: bool


@final
@dataclasses.dataclass
class _CacheItem(Generic[_R]):
    fut: asyncio.Future[_R]
    later_call: asyncio.Handle | None

    def cancel(self) -> None:
        if self.later_call is not None:
            self.later_call.cancel()
            self.later_call = None


@final
class _LRUCacheWrapper(Generic[_P, _R]):
    def __init__(
        self,
        fn: Callable[_P, _Coro[_R]],
        maxsize: int | None,
        typed: bool,
        ttl: float | None,
    ) -> None:
        if maxsize is not None and maxsize <= 0:
            raise ValueError("maxsize must be greater than 0 or None")
        with contextlib.suppress(AttributeError):
            self.__module__ = fn.__module__
        with contextlib.suppress(AttributeError):
            self.__name__ = getattr(fn, "__name__", fn.__class__.__name__)
        with contextlib.suppress(AttributeError):
            self.__qualname__ = getattr(fn, "__qualname__", fn.__class__.__name__)
        with contextlib.suppress(AttributeError):
            self.__doc__ = fn.__doc__
        with contextlib.suppress(AttributeError):
            self.__annotations__ = fn.__annotations__
        with contextlib.suppress(AttributeError):
            self.__dict__.update(fn.__dict__)
        # set __wrapped__ last so we don't inadvertently copy it
        # from the wrapped function when updating __dict__
        if hasattr(inspect, "markcoroutinefunction"):
            inspect.markcoroutinefunction(self)
        else:
            self._is_coroutine = getattr(asyncio.coroutines, "_is_coroutine", None)
        self.__wrapped__ = fn
        self.__maxsize = maxsize
        self.__typed = typed
        self.__ttl = ttl
        self.__cache: OrderedDict[Hashable, _CacheItem[_R]] = OrderedDict()
        self.__closed = False
        self.__hits = 0
        self.__misses = 0
        self.__tasks: set[asyncio.Task[_R]] = set()
        self.__cancelling_tasks: set[asyncio.Task[_R]] = set()
        self.__instance_cache_key = f"__alru_cache_{id(self)}"

    def __contains__(self, /, *args: Hashable, **kwargs: Any) -> bool:  # ruff: ignore[any-type]
        key = _make_key(args, kwargs, self.__typed)
        return key in self.__cache

    def set_size(self, maxsize: int) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be greater than 0")
        self.__maxsize = maxsize
        while len(self.__cache) > maxsize:
            _, item = self.__cache.popitem(last=False)
            item.cancel()

    def cache_invalidate(self, /, *args: Hashable, **kwargs: Any) -> bool:  # ruff: ignore[any-type]
        key = _make_key(args, kwargs, self.__typed)

        cache_item = self.__cache.pop(key, None)
        if cache_item is None:
            return False
        else:
            cache_item.cancel()
            return True

    def cache_clear(self) -> None:
        """Clear cached results and request cancellation of all pending work."""
        self.__hits = 0
        self.__misses = 0

        for c in self.__cache.values():
            c.cancel()
        self.__cache.clear()
        self._cache_cancel_tasks()

    def _cache_cancel_tasks(self) -> None:
        for task in self.__tasks:
            if not task.done() and task not in self.__cancelling_tasks:
                self.__cancelling_tasks.add(task)
                task.cancel()

    async def cache_close(self, *, wait: bool = False) -> None:
        self.__closed = True
        await self._cache_close(wait=wait)

    async def _cache_close(self, *, wait: bool = False) -> None:
        tasks = list(self.__tasks)
        if not wait:
            self._cache_cancel_tasks()

        await asyncio.gather(*tasks, return_exceptions=True)
        for item in self.__cache.values():
            item.cancel()
        self.__cache.clear()

    def cache_info(self) -> _CacheInfo:
        return _CacheInfo(
            self.__hits,
            self.__misses,
            self.__maxsize,
            len(self.__cache),
        )

    def cache_parameters(self) -> _CacheParameters:
        return _CacheParameters(
            maxsize=self.__maxsize,
            typed=self.__typed,
            tasks=len(self.__tasks),
            closed=self.__closed,
        )

    def _cache_hit(self, key: Hashable) -> None:
        self.__hits += 1
        self.__cache.move_to_end(key)

    def _cache_miss(self, key: Hashable) -> None:
        self.__misses += 1

    def _task_done_callback(self, fut: asyncio.Future[_R], key: Hashable, task: asyncio.Task[_R]) -> None:
        self.__tasks.discard(task)
        self.__cancelling_tasks.discard(task)

        if task.cancelled():
            self._cache_expire(key, fut)
            fut.cancel()
            return

        exc = task.exception()
        if exc is not None:
            self._cache_expire(key, fut)
            if not fut.done():
                fut.set_exception(exc)
                # The caller awaits its task directly; retrieve the cached failure too.
                fut.exception()
            return

        cache_item = self.__cache.get(key)
        if self.__ttl is not None and cache_item is not None and cache_item.fut is fut:
            loop = asyncio.get_running_loop()
            cache_item.later_call = loop.call_later(self.__ttl, self._cache_expire, key, fut)
        if not fut.done():
            fut.set_result(task.result())

    def _cache_expire(self, key: Hashable, fut: asyncio.Future[_R]) -> None:
        item = self.__cache.get(key)
        if item is not None and item.fut is fut:
            self.__cache.pop(key)
            item.cancel()

    async def __call__(self, /, *fn_args: _P.args, **fn_kwargs: _P.kwargs) -> _R:
        if self.__closed:
            raise RuntimeError(f"alru_cache is closed for {self}")

        loop = asyncio.get_running_loop()

        key = _make_key(fn_args, fn_kwargs, self.__typed)

        cache_item = self.__cache.get(key)

        if cache_item is not None and cache_item.fut.done():
            if not cache_item.fut.cancelled() and cache_item.fut.exception() is None:
                self._cache_hit(key)
                return cache_item.fut.result()
            else:
                # exception here
                cache_item = self.__cache.pop(key)
                cache_item.cancel()

        fut = loop.create_future()
        coro = self.__wrapped__(*fn_args, **fn_kwargs)
        task: asyncio.Task[_R] = loop.create_task(coro)
        self.__tasks.add(task)
        task.add_done_callback(partial(self._task_done_callback, fut, key))

        self.__cache[key] = _CacheItem(fut, None)

        if self.__maxsize is not None and len(self.__cache) > self.__maxsize:
            _, cache_item = self.__cache.popitem(last=False)
            cache_item.cancel()

        self._cache_miss(key)
        return await task

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> Self: ...

    @overload
    def __get__(
        self: _LRUCacheWrapper[Concatenate[_T, _P2], _R],
        instance: _T,
        owner: type[Any] | None = None,
    ) -> _LRUCacheWrapperInstanceMethod[_P2, _R, _T]: ...

    def __get__(
        self: Self,
        instance: _T | None,
        owner: type[Any] | None = None,
    ) -> Self | _LRUCacheWrapperInstanceMethod[_P2, _R, _T]:
        if instance is None:
            return self
        else:
            namespace = vars(instance)
            if self.__instance_cache_key not in namespace:
                wrapper = _LRUCacheWrapper(self.__wrapped__, self.__maxsize, self.__typed, self.__ttl)
                namespace.setdefault(self.__instance_cache_key, _LRUCacheWrapperInstanceMethod(wrapper, instance))
            return cast("_LRUCacheWrapperInstanceMethod[_P2, _R, _T]", namespace[self.__instance_cache_key])


@final
class _LRUCacheWrapperInstanceMethod(Generic[_P, _R, _T]):
    def __init__(
        self,
        wrapper: _LRUCacheWrapper[Any, _R],
        instance: _T,
    ) -> None:
        with contextlib.suppress(AttributeError):
            self.__module__ = wrapper.__module__
        with contextlib.suppress(AttributeError):
            self.__name__ = wrapper.__name__
        with contextlib.suppress(AttributeError):
            self.__qualname__ = wrapper.__qualname__
        with contextlib.suppress(AttributeError):
            self.__doc__ = wrapper.__doc__
        with contextlib.suppress(AttributeError):
            self.__annotations__ = wrapper.__annotations__
        with contextlib.suppress(AttributeError):
            self.__dict__.update(wrapper.__dict__)
        # set __wrapped__ last so we don't inadvertently copy it
        # from the wrapped function when updating __dict__
        if hasattr(inspect, "markcoroutinefunction"):
            inspect.markcoroutinefunction(self)
        else:
            self._is_coroutine = getattr(asyncio.coroutines, "_is_coroutine", None)
        self.__wrapped__ = wrapper.__wrapped__
        self.__instance = instance
        self.__wrapper = wrapper

    def __contains__(self, *args: Hashable, **kwargs: Any) -> bool:  # ruff: ignore[any-type]
        return self.__wrapper.__contains__(*args, **kwargs)

    def set_size(self, maxsize: int) -> None:
        self.__wrapper.set_size(maxsize)

    def cache_invalidate(self, /, *args: Hashable, **kwargs: Any) -> bool:  # ruff: ignore[any-type]
        return self.__wrapper.cache_invalidate(self.__instance, *args, **kwargs)

    def cache_clear(self) -> None:
        self.__wrapper.cache_clear()

    async def cache_close(self, *, wait: bool = False) -> None:
        """Drain this instance's method work while leaving its cache reusable."""
        await self.__wrapper._cache_close(wait=wait)

    def cache_info(self) -> _CacheInfo:
        return self.__wrapper.cache_info()

    def cache_parameters(self) -> _CacheParameters:
        return self.__wrapper.cache_parameters()

    async def __call__(self, /, *fn_args: _P.args, **fn_kwargs: _P.kwargs) -> _R:
        return await self.__wrapper(self.__instance, *fn_args, **fn_kwargs)


def _make_wrapper(
    maxsize: int | None,
    typed: bool,
    ttl: float | None = None,
) -> Callable[[_CBP[_P, _R]], _LRUCacheWrapper[_P, _R]]:
    def wrapper(fn: _CBP[_P, _R]) -> _LRUCacheWrapper[_P, _R]:
        origin = fn

        while isinstance(origin, (partial, partialmethod)):
            origin = origin.func

        if not inspect.iscoroutinefunction(origin):
            raise RuntimeError(f"Coroutine function is required, got {fn!r}")

        # functools.partialmethod support
        if hasattr(fn, "_make_unbound_method"):
            fn = cast("Any", fn)._make_unbound_method()

        return _LRUCacheWrapper(cast("_CB[_P, _R]", fn), maxsize, typed, ttl)

    return wrapper


@overload
def alru_cache(
    maxsize: int | None = 128,
    typed: bool = False,
    *,
    ttl: float | None = None,
) -> Callable[[_CBP[_P, _R]], _LRUCacheWrapper[_P, _R]]:
    """Decorator to wrap an asynchronous function with an LRU cache.

    Parameters
    ----------
    maxsize : int | None, optional
        Maximum cache size. If None, cache is unbounded.
    typed : bool, optional
        Whether arguments of different types are cached separately.
    ttl : float | None, optional
        Time-to-live in seconds for cache entries.

    Returns
    -------
    Callable
        A wrapper decorator for the coroutine function.
    """


@overload
def alru_cache(
    maxsize: _CBP[_P, _R],
    /,
) -> _LRUCacheWrapper[_P, _R]:
    """Decorator to wrap an asynchronous function with an LRU cache using default settings.

    Parameters
    ----------
    maxsize : Callable
        The coroutine function to decorate.

    Returns
    -------
    _LRUCacheWrapper
        The decorated async function.
    """


def alru_cache(
    maxsize: int | _CBP[_P, _R] | None = 128,
    typed: bool = False,
    *,
    ttl: float | None = None,
) -> Any:
    """Decorator to wrap an asynchronous function with an LRU cache.

    Parameters
    ----------
    maxsize : int | Callable | None, optional
        Maximum cache size. Can also be the function to decorate directly.
    typed : bool, optional
        Whether arguments of different types are cached separately.
    ttl : float | None, optional
        Time-to-live in seconds for cache entries.

    Returns
    -------
    Any
        The decorated wrapper or decorator function.
    """
    if maxsize is None or isinstance(maxsize, int):
        return _make_wrapper(maxsize, typed, ttl)
    else:
        fn = cast("_CB[_P, _R]", maxsize)

        if callable(fn) or hasattr(fn, "_make_unbound_method"):
            return _make_wrapper(128, False, None)(fn)

        raise NotImplementedError(f"{fn!r} decorating is not supported")


def parse_rpn_expression(expr: str) -> str:
    """Convert a Reverse Polish Notation (RPN) expression into a human-readable infix formula.

    Parameters
    ----------
    expr : str
        The space-separated RPN expression (e.g. 'EC 100 % 0 ==', 'SPIN_DIR 1 == SPIN_SEC 5 < &&').

    Returns
    -------
    str
        The human-readable infix expression (e.g. '(EC % 100) == 0', '(SPIN_DIR == 1) && (SPIN_SEC < 5)').
    """
    if not expr:
        return ""
    tokens = expr.strip().split()
    stack: list[tuple[str, bool]] = []

    for token in tokens:
        if token in _UNARY_OPS and len(stack) >= 1:
            operand, _ = stack.pop()
            if token in ("not", "!"):
                prefix = "not " if token == "not" else "!"
                rendered = f"{prefix}({operand})" if " " in operand else f"{prefix}{operand}"
                stack.append((rendered, token == "not"))
            elif token == "~":
                stack.append((f"~({operand})" if " " in operand else f"~{operand}", False))
        elif token in _BINARY_OPS and len(stack) >= 2:
            right, right_needs_grouping = stack.pop()
            left, left_needs_grouping = stack.pop()
            left = f"({left})" if left_needs_grouping else left
            right = f"({right})" if right_needs_grouping else right
            if token in _COMPARISON_OPS or token in _LOGICAL_OPS:
                stack.append((f"{left} {token} {right}", True))
            else:
                stack.append((f"({left} {token} {right})", False))
        else:
            stack.append((token, False))

    return stack[-1][0] if stack else expr
