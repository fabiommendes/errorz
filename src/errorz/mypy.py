from functools import partial
from typing import Callable

import rich
from mypy.plugin import AnalyzeTypeContext, FunctionContext, Plugin
from mypy.types import Type

type TypeAnaliser = Callable[[AnalyzeTypeContext], Type]
type FunctionAnalyser = Callable[[FunctionContext], Type]


class ResultPlugin(Plugin):
    def get_type_analyze_hook(self, fullname: str) -> TypeAnaliser | None:
        # if fullname == "errorz.Result":
        #     return analyse_result_type
        return None

    def get_function_hook(self, fullname: str) -> FunctionAnalyser | None:
        if fullname.startswith("builtins."):
            return None

        return partial(analyse_result_module_function, fullname)


def analyse_result_type(ctx: AnalyzeTypeContext) -> Type:
    if ctx.context.line not in lines:
        print(f"Analyzing type: {ctx.type}  {ctx.context.line}")
        lines.add(ctx.context.line)

    try:
        return ctx.api.analyze_type(ctx.type)
    except Exception:
        # print(f"Error analyzing type: {e}")
        return ctx.type


def analyse_result_module_function(name: str, ctx: FunctionContext) -> Type:
    if ctx.context.line < 840:
        return ctx.default_return_type

    print(f"Analyzing function: {name} (line {ctx.context.line})")
    rich.print(ctx)

    # print(vars(ctx))
    return ctx.default_return_type


def plugin(version: str) -> type[ResultPlugin]:
    print(f"Loading plugin for mypy version {version}")
    return ResultPlugin


lines: set[int] = {842, 843, 844}
