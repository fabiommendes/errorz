"""
Copyright (c) 2026, Fábio Macêdo Mendes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is the main errorz module. It is implemented in a single Python file to
help vendorizing it. It is distributed as a package, instead of a errorz.py file,
to allow for py.typed marker.
"""

from __future__ import annotations

import builtins
import functools
from collections import deque
from types import NotImplementedType
from typing import (
    Any,
    Callable,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Protocol,
    Self,
    TypeIs,
    TypeVar,
    cast,
    final,
    overload,
)

# Raised when trying to unwrap a None value. It is an alias for ValueError to allow
# mocking it in tests (or global mokey-patching if you are feelling adventurous).
UnwrapError = ValueError

__version__ = "0.1.0"
__author__ = "Fábio Macêdo Mendes"
__all__ = (
    "Result",
    "UnwrapError",
    "unwrap",
    "unwrap_lazy",
    "expect",
    "map",
    "coalesce",
    "filter",
    "zip",
    "some",
    "getattr",
    "call",
    "iter",
)

MISSING: NotImplementedType = cast(NotImplementedType, object())

E_co = TypeVar("E_co", covariant=True, default=Any, bound=object)
T_co = TypeVar("T_co", covariant=True)

# type Result[T_co, E_co = Any] = Err[E_co] | T_co
type Result[T, E = Any] = T | Err[E]


class Err(Generic[E_co]):
    """
    A simple error wrapper that implements the Error protocol. It is used to wrap
    error values in a way that they can be distinguished from regular values.
    """

    __is_errorz_error__ = True
    __match_args__ = ("error",)

    @property
    def error(self) -> E_co:
        return self._error

    def __init__(self, error: E_co) -> None:
        self._error = error

    def __repr__(self) -> str:
        return f"Err({self._error!r})"

    def __hash__[E: Hashable](self: Err[E]) -> int:
        return hash(self._error)

    #
    # Python magic methods
    #
    @final
    def __bool__(self) -> Literal[False]:
        return False

    # Arithmetic operations
    def __add__(self, other: Any) -> Self:
        return self

    def __radd__(self, other: Any) -> Self:
        return self

    def __mul__(self, other: Any) -> Self:
        return self

    def __rmul__(self, other: Any) -> Self:
        return self

    def __matmul__(self, other: Any) -> Self:
        return self

    def __rmatmul__(self, other: Any) -> Self:
        return self

    def __sub__(self, other: Any) -> Self:
        return self

    def __rsub__(self, other: Any) -> Self:
        return self

    def __truediv__(self, other: Any) -> Self:
        return self

    def __rtruediv__(self, other: Any) -> Self:
        return self

    def __floordiv__(self, other: Any) -> Self:
        return self

    def __rfloordiv__(self, other: Any) -> Self:
        return self

    def __mod__(self, other: Any) -> Self:
        return self

    def __rmod__(self, other: Any) -> Self:
        return self

    def __pow__(self, other: Any) -> Self:
        return self

    def __rpow__(self, other: Any) -> Self:
        return self

    def __or__(self, other: Any) -> Self:
        return self

    def __ror__(self, other: Any) -> Self:
        return self

    def __and__(self, other: Any) -> Self:
        return self

    def __rand__(self, other: Any) -> Self:
        return self

    def __xor__(self, other: Any) -> Self:
        return self

    def __rxor__(self, other: Any) -> Self:
        return self

    def __rshift__(self, other: Any) -> Self:
        return self

    def __rrshift__(self, other: Any) -> Self:
        return self

    def __lshift__(self, other: Any) -> Self:
        return self

    def __rlshift__(self, other: Any) -> Self:
        return self

    def __gt__(self, other: Any) -> Self:
        return self

    def __ge__(self, other: Any) -> Self:
        return self

    def __le__(self, other: Any) -> Self:
        return self

    def __lt__(self, other: Any) -> Self:
        return self

    #
    # Public methods
    #
    def exception(self) -> BaseException:
        """
        Return the error as an exception.

        Non-exceptional values are converted to a UnwrapError with self.error
        as an argument.
        """
        e = self._error
        if isinstance(e, BaseException):
            return e
        if isinstance(e, type) and issubclass(e, BaseException):
            return UnwrapError(e)
        return UnwrapError(e)


class Tagged[T, B: bool](NamedTuple):
    value: T
    is_error: B


type IsErr[E] = Tagged[E, Literal[True]]
type IsOk[T] = Tagged[T, Literal[False]]


def _any(x: object) -> Any:
    return x


_iter = builtins.iter
_getattr = builtins.getattr


#
# Constructors
#
@overload
def err[E](error: E, /) -> Result[Any, E]: ...


@overload
def err[T, E](error: E, /, type: type[T]) -> Result[T, E]: ...


def err(error: Any, /, type: Any = None) -> Any:
    """
    Creates an error value.

    Args:
        error: The error value to wrap.

    Examples:
        >>> rz.err('error') # type is Result[Any, str]
        Err('error')
        >>> rz.err('error', type=int) # type is Result[int, str]
        Err('error')
    """
    return Err(error)


@overload
def ok[T](value: T, /) -> Result[T, Any]: ...


@overload
def ok[T, E](value: T, /, err: type[E]) -> Result[T, E]: ...


def ok[T, E](value: Any, /, err: Any = None) -> Any:
    """
    Create a success value. This is just an identity function, but it can be used
    for symmetry with `err` and to make it clear that a value is intended to be a
    success value.

    You can also pass the type of the error case to appease the type checker.

    Args:
        value: The success value to return.

    Examples:
        >>> rz.ok(42) # type is Result[int, Any]
        42
        >>> rz.ok(42, err=str) # type is Result[int, str]
        42
    """
    return value


def is_err(value: Result[Any], /) -> TypeIs[Err]:
    """
    Check if the value is an error.

    Args:
        value: The result value to check.

    Examples:
        >>> rz.is_err(rz.err('error'))
        True
        >>> rz.is_err(42)
        False

    Notes:
        The corresponding is_ok() does not exist because typecheckers often struggle
        with type narrowing because Python type system do not include negative
        bounds (e.g. "T but not Err").

        The Err case evaluates to False. If you known that T is never falsy,
        you can just use the common Pythonic ways of checking for nullable
        values:

        >>> value = rz.err(42)
        >>> print(value or "error")
        error
        >>> if value:
        ...     print("This will never be an error case!")

        The same caveats of Optional types apply here.
    """
    return isinstance(value, Err)


def check[T](value: Result[T], /) -> TypeIs[T]:
    """
    Check if value is not an Err and return True.

    If the value is an error, raise it or a UnwrapError if E is not an exception.

    Args:
        value: The result value to validate.
    """
    if isinstance(value, Err):
        raise value.exception()
    return True


def tagged[T, E](value: Result[T, E], /) -> IsOk[T] | IsErr[E]:
    """
    Check if the value is an error and return False if it is, True otherwise.

    Args:
        value: The result value to check.

    Returns:
        True if the value is not an error, False otherwise.

    Examples:
        >>> rz.tagged(42)
        Tagged(value=42, is_error=False)
        >>> rz.tagged(rz.err('error'))
        Tagged(value='error', is_error=True)
    """
    if isinstance(value, Err):
        return cast("IsErr[E]", Tagged(value=value.error, is_error=True))
    return cast("IsOk[T]", Tagged(value=value, is_error=False))


#
# Unwrappers
#
def unwrap[T](value: Result[T], /, default: T = MISSING) -> T:
    """
    Unwrap a result.

    If the value is an error and no default is provided, raise the
    :meth:`Err.exception` method associated with it.

    Args:
        value: The result value to unwrap.

    Examples:
        >>> rz.unwrap(42)
        42
        >>> rz.unwrap(rz.err('error'))
        Traceback (most recent call last):
        ...
        ValueError: error

    See also:
        - :func:`rz.expect`
        - :func:`rz.unwrap_lazy`
    """
    if isinstance(value, Err):
        if default is MISSING:
            raise value.exception()
        return default
    return value


def unwrap_lazy[T](value: Result[T], /, default: Callable[[], T]) -> T:
    """
    Unwrap a value that may be None. If the value is None, return the result of
    calling the default function.

    This may be used instead of :func:`rz.unwrap` when the default value is
    expensive to compute or produces side effects.

    Args:
        value: The optional value to unwrap.
        default: The function to call if the optional value is None.

    Examples:
        >>> rz.unwrap_lazy(0, lambda: 42)
        0
        >>> rz.unwrap_lazy(rz.err('error'), lambda: 42)
        42

    See also:
        - :func:`rz.unwrap`
    """
    if isinstance(value, Err):
        if default is MISSING:
            raise value.exception()
        return default()
    return value


def expect[T](value: Result[T], /, error: str | BaseException) -> T:
    """
    Unwrap a value that may be None. If the value is None, raise the provided
    error or raises an UnwrapError (ValueError, usually) if a string is
    provided instead of an exception.

    Args:
        value: The optional value to unwrap.
        error: The error to raise if the value is None.

    Examples:
        >>> rz.expect(42, "Value is None")
        42
        >>> rz.expect(rz.err(ZeroDivisionError()), "Value is an error")
        Traceback (most recent call last):
        ...
        ValueError: Value is an error

    See also:
        - :func:`rz.unwrap`
    """
    if not isinstance(value, Err):
        return value
    elif isinstance(error, BaseException):
        raise error
    raise UnwrapError(error)


def extract[T, E](fn: Callable[[E], T], value: Result[T, E], /) -> T:
    """
    Extract the value from the result.

    If it is an error, transform it with the given function.

    Args:
        fn: The function to apply in case of errors.
        value: The result value to extract the error from.

    Examples:
        >>> rz.extract(lambda e: f"error: {e}", rz.err(42))
        'error: 42'
        >>> rz.extract(lambda e: str(e), "ok")
        'ok'
    """
    return fn(value.error) if isinstance(value, Err) else value


def unpack[T, E, R](
    value: Result[T, E], /, ok: Callable[[T], R], err: Callable[[E], R]
) -> R:
    """
    Unpack a result value using either the ok or err functions.

    This is useful for chaining operations that may return errors without having to
    check for errors at each step.

    Args:
        value:
            The result value to unpack.
        ok:
            The function to apply if the value is an ok value.
        err:
            The function to apply if the value is an error.

    Examples:
        >>> rz.unpack(rz.err("error"), ok=str, err=str.upper)
        'ERROR'
        >>> rz.unpack(42, ok=str, err=str.upper)
        '42'

    Notes:
        This can be used as a poor-man's match statement. Real match statements
        are supported, but there is no explicit Ok() case:

        >>> result = rz.err("error")
        >>> match result:
        ...     case rz.Err(error):
        ...         pass # code in the error case
        ...     case value:
        ...         pass # code in the ok case
    """
    return err(value.error) if isinstance(value, Err) else ok(value)


def to_optional[T](value: Result[T, Any]) -> Optional[T]:
    """
    Convert a Result to an Optional by converting any error to None.

    Args:
        value: The result value to convert.

    Returns:
        An Optional containing the unwrapped value if it is Ok, or None if it
        is an Err.
    """
    if isinstance(value, Err):
        return None
    return value


def error[Any, E](value: Result[Any, E], /) -> Optional[E]:
    """
    Get the error value if the result is an error, None otherwise.

    Args:
        value: The result value to check.
    Examples:
        >>> rz.error(42) is None
        True
        >>> rz.error(rz.err('error'))
        'error'
    """
    if isinstance(value, Err):
        return value.error
    return None


def swap[T, E](value: Result[T, E], /) -> Result[E, T]:
    """
    Swap the ok and error values of a result.

    Args:
        value: The result value to swap.
    Examples:
        >>> rz.swap(42)
        Err(42)
        >>> rz.swap(rz.err('error'))
        'error'
    """
    if isinstance(value, Err):
        return value.error
    return Err(value)


@overload
def map[T, E, R](fn: Callable[[T], R], value: Result[T, E], /) -> Result[R, E]: ...


@overload
def map[T1, T2, E, R](
    fn: Callable[[T1, T2], R], x1: Result[T1, E], x2: Result[T2, E], /
) -> Result[R, E]: ...


@overload
def map[T1, T2, T3, E, R](
    fn: Callable[[T1, T2, T3], R],
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    /,
) -> Result[R, E]: ...


@overload
def map[T1, T2, T3, T4, E, R](
    fn: Callable[[T1, T2, T3, T4], R],
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    /,
) -> Result[R, E]: ...


@overload
def map[T1, T2, T3, T4, T5, E, R](
    fn: Callable[[T1, T2, T3, T4, T5], R],
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    /,
) -> Result[R, E]: ...


@overload
def map[T1, T2, T3, T4, T5, T6, E, R](
    fn: Callable[[T1, T2, T3, T4, T5, T6], R],
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    /,
) -> Result[R, E]: ...


@overload
def map[T1, T2, T3, T4, T5, T6, T7, E, R](
    fn: Callable[[T1, T2, T3, T4, T5, T6, T7], R],
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    /,
) -> Result[R, E]: ...


@overload
def map[T1, T2, T3, T4, T5, T6, T7, T8, E, R](
    fn: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], R],
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    x8: Result[T8, E],
    /,
) -> Result[R, E]: ...


def map(fn: Any, *values: Any) -> Any:
    """
    Apply the function to the values if none of them are errors, otherwise
    return the first error found.


    Args:
        fn:
            The function to apply to the values if none of them are errors.
        x1, x2, ...:
            The result values to apply the function to.
            It accepts any number of arguments (but only type checks up to 8).

    Examples:
        >>> rz.map(lambda x: x + 1, 41)
        42
        >>> rz.map(lambda x, y: x + y, 40, 2)
        42
        >>> rz.map(lambda x, y: x + y, 42, rz.err('error'))
        Err('error')

    See also:
        - :func:`rz.zip`
    """
    if any(is_err(value) for value in values):
        return next(value for value in values if is_err(value))
    return fn(*values)


def map_err[T, E, R](fn: Callable[[E], R], value: Result[T, E], /) -> Result[T, R]:
    """
    Apply the function to the error value if it is an error, otherwise return
    the ok value.

    Args:
        fn:
            The function to apply to the error case.
        value:
            The result value to check.

    Examples:
        >>> rz.map_err(lambda e: f"error: {e}", rz.err(42))
        Err('error: 42')
        >>> rz.map_err(lambda e: f"error: {e}", 42)
        42
    """
    if isinstance(value, Err):
        return Err(fn(value.error))
    return value


@overload
def coalesce[T, E](values: Iterable[Result[T, E]], /) -> Result[T, E]: ...


@overload
def coalesce[T1, T2, E1, E2](
    x1: Result[T1, E1], x2: Result[T2, E2], /
) -> Result[T1 | T2, E1 | E2]: ...


@overload
def coalesce[T1, T2, T3, E](
    x1: Result[T1, E], x2: Result[T2, E], x3: Result[T3, E], /
) -> Result[T1 | T2 | T3, E]: ...


@overload
def coalesce[T1, T2, T3, T4, E](
    x1: Result[T1, E], x2: Result[T2, E], x3: Result[T3, E], x4: Result[T4, E], /
) -> Result[T1 | T2 | T3 | T4, E]: ...


@overload
def coalesce[T1, T2, T3, T4, T5, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5, E]: ...


@overload
def coalesce[T1, T2, T3, T4, T5, T6, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5 | T6, E]: ...


@overload
def coalesce[T1, T2, T3, T4, T5, T6, T7, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5 | T6 | T7, E]: ...


@overload
def coalesce[T1, T2, T3, T4, T5, T6, T7, T8, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    x8: Result[T8, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8, E]: ...


def coalesce(*values: Any) -> Any:
    """
    Return the first value that is not an error, or the last error if all values
    are errors.

    This function works as short-circuiting "or" as if Ok values are thruthy
    and Err values are falsy.

    Examples:
        >>> rz.coalesce(rz.err("e1"), rz.err("e2"), 42, 43, ...)
        42
        >>> rz.coalesce(rz.err("e1"), rz.err("e2"))
        Err('e2')
        >>> rz.coalesce([rz.err("e1"), rz.err("e2"), 42, 43, ...])
        42

    See also:
        - :func:`rz.zip`
        - :func:`rz.all`
    """
    if len(values) == 1:
        values = values[0]

    value: Any = None
    for value in values:
        if not isinstance(value, Err):
            return value
    if value is None:
        raise ValueError("coalesce() expected at least one value")
    return value


@overload
def all[T, E](values: Iterable[Result[T, E]], /) -> Result[T, E]: ...


@overload
def all[T1, T2, E1, E2](
    x1: Result[T1, E1], x2: Result[T2, E2], /
) -> Result[T1 | T2, E1 | E2]: ...


@overload
def all[T1, T2, T3, E](
    x1: Result[T1, E], x2: Result[T2, E], x3: Result[T3, E], /
) -> Result[T1 | T2 | T3, E]: ...


@overload
def all[T1, T2, T3, T4, E](
    x1: Result[T1, E], x2: Result[T2, E], x3: Result[T3, E], x4: Result[T4, E], /
) -> Result[T1 | T2 | T3 | T4, E]: ...


@overload
def all[T1, T2, T3, T4, T5, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5, E]: ...


@overload
def all[T1, T2, T3, T4, T5, T6, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5 | T6, E]: ...


@overload
def all[T1, T2, T3, T4, T5, T6, T7, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5 | T6 | T7, E]: ...


@overload
def all[T1, T2, T3, T4, T5, T6, T7, T8, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    x8: Result[T8, E],
    /,
) -> Result[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8, E]: ...


def all(*values: Any) -> Any:
    """
    Return the first error in the arguments. If no argument is an error, return
    the last ok value.

    This function works as short-circuiting "and" as if Ok values are thruthy
    and Err values are falsy.

    Args:
        x1, x2, ...:
            The result values to check.
            It accepts any number of arguments (but only type checks up to 8).

    Examples:
        >>> rz.all(1, 2, 3)
        3
        >>> rz.all(1, rz.err("e1"), rz.err("e2"))
        Err('e1')

    See also:
        - :func:`rz.coalesce`
    """
    if len(values) == 1:
        values = values[0]

    if len(values) == 1:
        values = values[0]

    for value in values:
        if isinstance(value, Err):
            return value
    try:
        return value  # pyright: ignore[reportPossiblyUnboundVariable]
    except NameError:
        raise ValueError("all() expected at least one value")


@overload
def zip[T1, T2, E](
    x1: Result[T1, E], x2: Result[T2, E], /
) -> Result[tuple[T1, T2], E]: ...


@overload
def zip[T1, T2, T3, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    /,
) -> Result[tuple[T1, T2, T3], E]: ...


@overload
def zip[T1, T2, T3, T4, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    /,
) -> Result[tuple[T1, T2, T3, T4], E]: ...


@overload
def zip[T1, T2, T3, T4, T5, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    /,
) -> Result[tuple[T1, T2, T3, T4, T5], E]: ...


@overload
def zip[T1, T2, T3, T4, T5, T6, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    /,
) -> Result[tuple[T1, T2, T3, T4, T5, T6], E]: ...


@overload
def zip[T1, T2, T3, T4, T5, T6, T7, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    /,
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7], E]: ...


@overload
def zip[T1, T2, T3, T4, T5, T6, T7, T8, E](
    x1: Result[T1, E],
    x2: Result[T2, E],
    x3: Result[T3, E],
    x4: Result[T4, E],
    x5: Result[T5, E],
    x6: Result[T6, E],
    x7: Result[T7, E],
    x8: Result[T8, E],
    /,
) -> Result[tuple[T1, T2, T3, T4, T5, T6, T7, T8], E]: ...


def zip(*args: Any) -> Any:
    """
    Return a tuple if no argument is an error and the first error otherwise.

    Args:
        x1, x2, ...:
            The optional values to check.
            It accepts any number of arguments (but only type checks up to 8).

    Examples:
        >>> rz.zip(1, 2, 3)
        (1, 2, 3)
        >>> rz.zip(1, 2, rz.err('error'))
        Err('error')

    """
    for arg in args:
        if isinstance(arg, Err):
            return arg
    return args


class Caller[**P, R](Protocol):
    def __call__(
        self, fn: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
    ) -> R: ...


class _CallFactory:
    """
    Call the optional function with the given arguments or return the error.

    Args:
        fn: The fallible function to call.
        *args: The positional arguments to pass to the function.
        **kwargs: The keyword arguments to pass to the function.

    Examples:
        >>> rz.call(lambda x: x + 1, 41)
        42
        >>> rz.call(rz.err('error'), 40, 2)
        Err('error')

        We can assign the error type using the indexing notation.

        >>> rz.call[ZeroDivisionError](lambda x: 1 / x, 0)
        Err(ZeroDivisionError('division by zero'))
    """

    @overload
    def __getitem__[E: Exception, R, **P](
        self, type: type[E]
    ) -> Caller[P, Result[R, E]]: ...

    @overload
    def __getitem__[E1: Exception, E2: Exception, R, **P](
        self, type: tuple[type[E1], type[E2]]
    ) -> Caller[P, Result[R, E1 | E2]]: ...

    @overload
    def __getitem__[E1: Exception, E2: Exception, E3: Exception, R, **P](
        self, type: tuple[type[E1], type[E2], type[E3]]
    ) -> Caller[P, Result[R, E1 | E2 | E3]]: ...

    @overload
    def __getitem__[E1: Exception, E2: Exception, E3: Exception, E4: Exception, R, **P](
        self, type: tuple[type[E1], type[E2], type[E3], type[E4]]
    ) -> Caller[P, Result[R, E1 | E2 | E3 | E4]]: ...

    @overload
    def __getitem__[E: Exception, R, **P](
        self, type: tuple[E, ...]
    ) -> Caller[P, Result[R, E]]: ...

    def __getitem__(self, type: Any) -> Any:
        def call(*args: Any, **kwargs: Any) -> Any:
            return call_checked(type, *args, **kwargs)

        try:
            call.__name__ = f"call[{type.__name__}]"
        except AttributeError:  # type is given as a tuple
            call.__name__ = "call[...]"

        return call

    def __call__[**P, R](
        self, fn: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
    ) -> Result[R, BaseException]:
        if isinstance(fn, Err):
            return fn
        try:
            return fn(*args, **kwargs)
        except BaseException as e:
            return Err(e)


call = _CallFactory()


def call_checked[**P, R, E: Exception](
    errors: type[E] | tuple[type[E], ...],
    fn: Callable[P, R],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> Result[R, E]:
    """
    Call the function with the given arguments and catch any exception of the given type.

    Args:
        exception: The type of exception to catch and return as an error.
        fn: The function to call.
        *args: The positional arguments to pass to the function.
        **kwargs: The keyword arguments to pass to the function.

    Examples:
        >>> rz.call_checked(ZeroDivisionError, lambda x: 1 / x, 0)
        Err(ZeroDivisionError('division by zero'))
        >>> rz.call_checked(ValueError, lambda x: 1 / x, 0)
        Traceback (most recent call last):
        ...
        ZeroDivisionError: division by zero
    """
    try:
        return fn(*args, **kwargs)
    except BaseException as e:
        if isinstance(e, errors):
            return Err(e)
        raise e


@overload
def safe[**P, R]() -> Callable[[Callable[P, R]], Callable[P, Result[R, Exception]]]: ...


@overload
def safe[E: Exception, **P, R](
    exception: type[E], /
) -> Callable[[Callable[P, R]], Callable[P, Result[R, E]]]: ...


@overload
def safe[E1: Exception, E2: Exception, R, **P](
    exception: tuple[type[E1], type[E2]], /
) -> Callable[[Callable[P, R]], Callable[P, Result[R, E1 | E2]]]: ...


@overload
def safe[E1: Exception, E2: Exception, E3: Exception, R, **P](
    exception: tuple[type[E1], type[E2], type[E3]], /
) -> Callable[[Callable[P, R]], Callable[P, Result[R, E1 | E2 | E3]]]: ...


@overload
def safe[E1: Exception, E2: Exception, E3: Exception, E4: Exception, R, **P](
    exception: tuple[type[E1], type[E2], type[E3], type[E4]], /
) -> Callable[[Callable[P, R]], Callable[P, Result[R, E1 | E2 | E3 | E4]]]: ...


@overload
def safe[E: Exception, R, **P](
    exception: Iterable[type[E]], /
) -> Callable[[Callable[P, R]], Callable[P, Result[R, E]]]: ...


@overload
def safe(*args: Any) -> Any: ...


def safe(*errors: Any) -> Any:
    if not errors:
        return lambda fn: _wrap_safe(
            fn, lambda *args, **kwargs: call(fn, *args, **kwargs)
        )
    else:
        return lambda fn: _wrap_safe(
            fn, lambda *args, **kwargs: call_checked(errors, fn, *args, **kwargs)
        )


def getattr[T, R: type, E](
    obj: Result[T, E], attr: str, *, type: type[R] = _any(None)
) -> Result[R, E | AttributeError]:
    """
    Get the attribute of an object if it is not None, otherwise return None.

    It raises an AttributeError if the attribute do not exist.

    You can optionally specify the expected result type to get better type checking.

    Args:
        obj: The optional object to get the attribute from.
        attr: The name of the attribute to get.
        type: The expected type of the attribute (optional).

    Examples:
        >>> rz.getattr(42, "real")
        42
        >>> rz.getattr(rz.err('error'), "imag")
        Err('error')
        >>> rz.getattr(42, "non_existent")
        Err(AttributeError('non_existent'))
    """
    if isinstance(obj, Err):
        return Err(obj.error)

    try:
        value = cast("R", _getattr(obj, attr))
    except AttributeError:
        return Err(AttributeError(attr))
    if type is not None and not isinstance(value, type):
        msg = (
            f"Expected attribute {attr} to be of type {type}, "
            f"got {builtins.type(value)}"
        )
        raise TypeError(msg)
    return value


def _wrap_safe[F: Callable[..., Any]](fn: Any, impl: F) -> F:
    try:
        functools.update_wrapper(impl, fn)
    except Exception:
        return impl
    ret_type = impl.__annotations__.get("return", None)
    if ret_type is not None:
        impl.__annotations__["return"] = Result[ret_type, Exception]  # type: ignore
    return impl


#
# Lists, iterators, and other collections
#
def some[T, E](value: Result[T, E]) -> Iterable[T]:
    """
    Yield nothing or the ok value, if it exists.

    Args:
        value: The fallible value to yield.

    Examples:
        >>> list(rz.some(42))
        [42]
        >>> list(rz.some(rz.err('error')))
        []
    """
    if not isinstance(value, Err):
        yield value


def iter[T, E](value: Result[Iterable[T], E]) -> Iterable[T]:
    """
    Yield nothing or the elements of an iterable.

    Args:
        value: The fallible iterable to yield from.

    Examples:
        >>> list(rz.iter([42]))
        [42]
        >>> list(rz.iter(rz.err('error')))
        []
    """
    if not isinstance(value, Err):
        yield from value


def filter[T, E](seq: Iterable[Result[T, E]], /) -> Iterable[T]:
    """
    Return an iterable of the non-error values in the given sequence.

    Args:
        seq: The sequence of fallible values to filter.

    Examples:
        >>> list(rz.filter([1, 2, rz.err('error'), 3]))
        [1, 2, 3]
        >>> list(rz.filter([rz.err("error 1"), rz.err("error 2")]))
        []
    """
    return (x for x in seq if not isinstance(x, Err))


def partition[T, E](seq: Iterable[Result[T, E]], /) -> tuple[Iterable[T], Iterable[E]]:
    """
    Partition the given sequence into two sequence: one of non-error values and one of error values.

    Args:
        seq: The sequence of fallible values to partition.

    Examples:
        >>> oks, errs = rz.partition([1, 2, rz.err('error'), 3])
        >>> list(oks)
        [1, 2, 3]
        >>> list(errs)
        ['error']
    """
    next = _iter(seq).__next__
    seen_values = deque["T"]()
    seen_errors = deque["E"]()

    def oks() -> Iterator[T]:
        while True:
            try:
                if seen_values:
                    yield seen_values.popleft()
                    continue
                if isinstance(value := next(), Err):
                    seen_errors.append(value.error)
                    continue
                yield value
            except StopIteration:
                return

    def errors() -> Iterator[E]:
        while True:
            try:
                if seen_errors:
                    yield seen_errors.popleft()
                    continue
                if isinstance(value := next(), Err):
                    seen_errors.append(value.error)
                    continue
                seen_values.append(value)
            except StopIteration:
                return

    # Is it faster to use itertools.tee?
    return oks(), errors()


def combine[T, E](seq: Iterable[Result[T, E]], /) -> Result[list[T], E]:
    """
    Combine the given sequence of fallible values into a single list if all
    values are non-errors.

    Return the first error found otherwise.

    Args:
        seq: The sequence of fallible values to combine.

    Examples:
        >>> rz.combine([1, 2, 3])
        [1, 2, 3]
        >>> rz.combine([1, 2, rz.err('error')])
        Err('error')
    """
    values = []
    for value in seq:
        if isinstance(value, Err):
            return value
        values.append(value)
    return values


def filter_values[K, V, E](seq: Mapping[K, Result[V, E]], /) -> dict[K, V]:
    """
    Remove all Err values from the given mapping.

    Args:
        seq: The mapping of fallible values to filter.

    Examples:
        >>> rz.filter_values({'a': 1, 'b': rz.err('error'), 'c': 3})
        {'a': 1, 'c': 3}
        >>> rz.filter_values({'a': rz.err("error 1"), 'b': rz.err("error 2")})
        {}
    """
    return {k: v for k, v in seq.items() if not isinstance(v, Err)}


@overload
def non_empty[T](seq: Iterable[T], /) -> Result[list[T], IndexError]: ...


@overload
def non_empty[T, E](seq: Iterable[T], /, error: E) -> Result[list[T], E]: ...


def non_empty[T](seq: Iterable[T], /, error: Any = MISSING) -> Result[list[T], Any]:
    """
    Return the given sequence if it contains at least one non-error value, or an Error otherwise.

    Args:
        seq: The sequence of values to check.
        error: The error to return if the sequence is empty (defaults to IndexError).

    Examples:
        >>> rz.non_empty([1, 2, 3])
        [1, 2, 3]
        >>> rz.non_empty([])
        Err(IndexError(...))
        >>> rz.non_empty([], error="Sequence is empty")
        Err('Sequence is empty')
    """
    values = list(seq)
    if values:
        return values
    if error is MISSING:
        return Err(cast(Any, IndexError("Sequence is empty")))
    return Err(error)


@overload
def single[T](seq: Iterable[T], /) -> Result[T, IndexError]: ...


@overload
def single[T, E](seq: Iterable[T], /, error: E) -> Result[T, E]: ...


def single[T](seq: Iterable[T], /, error: Any = MISSING) -> Result[T, Any]:
    """
    Return the single element in the given sequence, or an Error otherwise.

    Args:
        seq: The sequence of values to check.
        error: The error to return if the sequence does not contain exactly one non-error value (defaults to IndexError).

    Examples:
        >>> rz.single([42])
        42
        >>> rz.single([])
        Err(IndexError(...))
        >>> rz.single([1, 2])
        Err(IndexError(...))
        >>> rz.single([], error="No single value")
        Err('No single value')
    """
    it = _iter(seq)
    try:
        value = next(it)
    except StopIteration:
        if error is MISSING:
            return Err(cast(Any, IndexError("Sequence is empty")))
        return Err(error)
    try:
        next(it)
        if error is MISSING:
            return Err(cast(Any, IndexError("Sequence contains more than one value")))
        return Err(error)
    except StopIteration:
        return value
