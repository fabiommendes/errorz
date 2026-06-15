# Errorz

Python officially handle errors using exceptions. This library provides a
lightweight approach inspired by the `Result` type used in Rust and other
functional programming languages: `Result` is an union between a success value 
and an error value.

The main advantage over exceptions is that they are expressed as values in the
type system. This allows for better static guarantees and make code more
explicit and easier to compose, since results are just like any other value that
can be passed around and manipulated without cluncky try/catch blocks.
Exceptions also break control flow and can be easily forgotten and lead to
crashes and brittle refactorings.

The cannonical way to implement this pattern is to use a tagged union of `Ok[T]`
and `Err[E]`. This is what Rust and Haskell do and there are some Python
libraries that follow this approach, e.g.,
[returns](https://returns.readthedocs.io/). However, Python don't have native
tagged unions and using them often feels unergnomic and non-Pythonic. This
library explores a more lightweight approach that defines `Result[T, E] = T |
Error[E]`, where `Error[E]` is a special abstract wrapper around an error value.
This is simular to the approach we used in the
[optionz](https://optionz.readthedocs.io/) library for nullables, where it was
more lightweight and in line with established Python idioms.

## Installation

Install Errorz using pip/uv/poetry whatever you like. For example:

```bash
pip install errorz
```
    
Errorz consists of a single file, so you can also just copy the `__init__.py`
file to your project as `errorz.py` and import it from there. Our special Error 
wrapper is defined as a protocol and has some special structure to ensure that
different copies of the vendorized lib can coexist without conflicts.


## Usage

Import `err` and use the functions as needed. 

```python
import errorz as rz

rz.unwrap(42) # 42
rz.unwrap(rz.err("error")) # raises ValueError
```

## Documentation

The documentation is available at https://optionz.rtfd.io/ and includes more 
examples and explanations of the functions provided by the library.

## License

Optionz is licensed under the MIT License. See [LICENSE](LICENSE) for more details.