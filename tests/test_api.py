import doctest

import errorz as rz


def test_doctests() -> None:
    result = doctest.testmod(
        rz,
        globs={"rz": rz},
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
    )
    assert result.attempted > 0, "No doctests were found"
    assert result.failed == 0, f"{result.failed} doctests failed"


def test_arithmetic_operations_with_error_types() -> None:
    e = rz.err("error")
    exprs = [
        e + 1,
        1 + e,
        e - 1,
        1 - e,
        e * 1,
        1 * e,
        e / 1,
        1 / e,
        e // 1,
        1 // e,
        e % 1,
        1 % e,
        e**1,
        1**e,
        e @ 1,
        1 @ e,
        1 << e,
        e << 1,
        1 >> e,
        e >> 1,
        e | 1,
        1 | e,
        e & 1,
        1 & e,
        e ^ 1,
        1 ^ e,
        e > 1,
        1 > e,
        e < 1,
        1 < e,
        e >= 1,
        1 >= e,
    ]
    for expr in exprs:
        assert expr == e


def test_normalize_exception() -> None:
    e1 = rz.err(ValueError)
    assert isinstance(e1.exception(), ValueError)

    e2 = rz.err(ValueError())
    assert isinstance(e2.exception(), ValueError)
