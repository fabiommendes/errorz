# Errorz

The canonical way to handle errors in Python is using exceptions. This library
provides a lightweight approach inspired by the `Result` type used in many
functional programming languages and Rust: `Result` is an union between a
success value and an error value.

`Result`s are expressed as values in the type system. This allows for better
static guarantees and make code more explicit and easier to compose. Errors are
handled just like any other value and can be passed around and manipulated
without clunky try/catch blocks. Exceptions also break control flow, and can
make the code hard to follow and brittle to refactor.

The usual way to implement `Result` is to use a tagged union of `Ok[T]` and
`Err[E]`. This is what Rust, Haskell and many other languages do. There are some
Python libraries that follow this approach, e.g.,
[returns](https://returns.readthedocs.io/), but I always felt them a little bit
non-ergonomic in Python. This library explores a more lightweight approach that
defines `Result[T, E] = T | Err[E]`, where `Err[E]` is a special wrapper around
an error value. The "ok" case just stands as flat value and do not require any
special wrapping and unwrapping.

We used a similar approach for nullables in 
[optionz](https://optionz.readthedocs.io/), and you might want to use both 
libraries together.

## Installation

Install Errorz using pip/uv/poetry whatever you like. For example:

```bash
pip install errorz
```

## Usage

The `Result[T, E]` represents a computation that may succeed with a value of
type `T` or fail with an error of type `E`. Often, `E` will be a subclass of
`Exception`, which is the standard way of representing errors in Python, but 
this is not required.

We create success and error values using the `ok` and `err` functions:

```python
import errorz as rz
from errorz import Result, Err

sucess = rz.ok(42) 
failure = rz.err("error") 
```

`errorz.ok` simply returns the value you pass to it, but tells the type checker
the return value is a `Result[T, E]` instead of just `T`. `errorz.err` wraps the 
error in the `Err` wrapper.

We often use results in a `match` statement or with `is_err` checks:

```python
match result: 
    case Err(error):
        print(f"Error: {error}")
    case value:
        print(f"Success: {value}")

# The alternative using if statements
if rz.is_err(result):
    print(f"Error: {result.error}")
else:
    print(f"Success: {result}")
```

You can also unwrap the result and let any exceptions propagate:

```python
rz.unwrap(success) # 42
rz.unwrap(failure) # raises ValueError
```

This library encourages to write code that does not use these kinds of checks
and constant wrapping/unwrapping. We implement functions that take `Results`
and implement the separate cases for you. For example, `errorz.map` applies a function 
if all arguments succeeded, otherwise it returns the first error:

```python
def add(x: int, y: int) -> int:
    return x + y

rz.map(add, success, success) # 42 + 42
rz.map(add, success, failure) # Err("error")
```

In the [API documentation](https://errorz.readthedocs.io/en/latest/api.html) you can find other similar utility functions.

When interacting with exception-throwing code, you can use `errorz.call_checked` to catch exceptions and return them as errors:

```python





## Documentation

The documentation is available at https://optionz.rtfd.io/ and includes more 
examples and explanations of the functions provided by the library.

## License

Optionz is licensed under the MIT License. See [LICENSE](LICENSE) for more details.