from string import ascii_letters, digits
from typing import Any, Iterable, cast

from hypothesis import strategies as st
from hypothesis.strategies import DrawFn

import errorz as rz

EXCEPTION_LIST = [Exception, ValueError, TypeError, KeyError, IndexError]

__all__ = ["result", "exceptions", "errors", "error_messages"]


@st.composite
def result[T, E = Any](
    draw: DrawFn, value: st.SearchStrategy[T], error: st.SearchStrategy[E] | None = None
) -> rz.Result[T, E]:
    """
    Generate Results with random values.

    Args:
        value:
            A strategy to generate the ok values.
        error:
            A strategy to generate the err values.
            If None is given, it will generate random exceptions or primitive values as errors.
    """

    is_ok = draw(st.booleans())
    if is_ok:
        return rz.ok(draw(value))
    elif error:
        return rz.err(draw(error))
    else:
        return cast(
            "rz.Err[E]",
            rz.err(
                draw(
                    st.one_of(
                        error_messages(),
                        exceptions(),
                        st.integers(),
                    )
                )
            ),
        )


def exceptions(
    exceptions: Iterable[type[Exception]] | None = None,
) -> st.SearchStrategy[Exception]:
    """
    Generate exceptions with random messages.

    By default, it generates a random exception from builtin python exceptions
    with a random message.

    You can also provide a custom list of exception classes to choose from.
    They must accept a single string argument in their constructor.
    """
    if exceptions is None:
        exceptions = EXCEPTION_LIST

    return st.one_of([st.builds(exc, error_messages()) for exc in exceptions])


def errors[E = Exception](
    error: st.SearchStrategy[E] | None = None,
) -> st.SearchStrategy[rz.Err[E]]:
    """
    Generate random error values.

    By default, it generates random exceptions with random messages.
    """
    value = cast("st.SearchStrategy[E]", error or exceptions())
    return value.map(rz.Err)


def error_messages() -> st.SearchStrategy[str]:
    """
    Generate random error messages.

    Those are small strings with common letters. We are not trying to stress
    test the string handling capabilities of our error types.

    If you want to stress test this, use the builtin st.text() strategy.
    """
    return st.one_of(
        st.sampled_from(["error", "fail", "invalid", "..."]),
        st.text(
            alphabet=ascii_letters + digits + " ",
            max_size=5,
        ),
    )
