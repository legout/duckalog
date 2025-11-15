"""Minimal Typer-compatible shim for environments without the real dependency."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union, get_args, get_origin, get_type_hints

import click


class Exit(click.exceptions.Exit):
    """Raised to exit the CLI early."""


def echo(message: str, err: bool = False) -> None:
    click.echo(message, err=err)


class OptionInfo:
    def __init__(self, default: Any, names: Tuple[str, ...], kwargs: Dict[str, Any]) -> None:
        self.default = default
        self.names = names
        self.kwargs = kwargs


class ArgumentInfo:
    def __init__(self, default: Any, kwargs: Dict[str, Any]) -> None:
        self.default = default
        self.kwargs = kwargs


def Option(default: Any = None, *names: str, **kwargs: Any) -> OptionInfo:
    return OptionInfo(default, names, kwargs)


def Argument(default: Any = ..., **kwargs: Any) -> ArgumentInfo:
    return ArgumentInfo(default, kwargs)


class Typer(click.Group):
    def __init__(self, *, help: Optional[str] = None) -> None:
        super().__init__(help=help)

    def command(self, name: Optional[str] = None, *, help: Optional[str] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            cmd_name = name or func.__name__.replace("_", "-")
            params = _build_params(func)
            click_command = click.Command(cmd_name, params=params, callback=func, help=help)
            self.add_command(click_command)
            return func

        return decorator

    def callback(self) -> Callable:
        parent_callback = super().callback

        def decorator(func: Callable) -> Callable:
            parent_callback()(func)
            return func

        return decorator


def _build_params(func: Callable) -> Sequence[click.Parameter]:
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    params: list[click.Parameter] = []
    for param in sig.parameters.values():
        default = param.default
        annotation = type_hints.get(param.name, param.annotation)
        if isinstance(default, OptionInfo):
            params.append(_build_option(param, annotation, default))
        else:
            arg_info = default if isinstance(default, ArgumentInfo) else ArgumentInfo(default, {})
            params.append(_build_argument(param, annotation, arg_info))
    return params


def _build_option(param: inspect.Parameter, annotation: Any, info: OptionInfo) -> click.Option:
    names = info.names or (f"--{param.name.replace('_', '-')}" ,)
    param_kwargs = dict(info.kwargs)
    click_type = _annotation_to_click_type(annotation, param_kwargs)
    if click_type is not None:
        param_kwargs["type"] = click_type
    if _is_bool_annotation(annotation) and "is_flag" not in param_kwargs:
        param_kwargs["is_flag"] = True
    if "help" not in param_kwargs and param.annotation is not inspect._empty:
        param_kwargs["show_default"] = True
    return click.Option(list(names), default=info.default, **param_kwargs)


def _build_argument(param: inspect.Parameter, annotation: Any, info: ArgumentInfo) -> click.Argument:
    param_kwargs: Dict[str, Any] = {}
    default = info.default
    required = default in (inspect._empty, ...)  # type: ignore[comparison-overlap]
    if not required and default is not inspect._empty and default is not ...:
        param_kwargs["default"] = default
    param_kwargs["required"] = required
    click_type = _annotation_to_click_type(annotation, info.kwargs)
    if click_type is not None:
        param_kwargs["type"] = click_type
    return click.Argument([param.name], **param_kwargs)


def _annotation_to_click_type(annotation: Any, extra: Dict[str, Any]) -> Optional[click.ParamType]:
    if _is_path_annotation(annotation):
        path_kwargs = {}
        for key in ("exists", "file_okay", "dir_okay", "writable", "readable", "resolve_path"):
            if key in extra:
                path_kwargs[key] = extra.pop(key)
        return click.Path(**path_kwargs)
    return None


def _is_path_annotation(annotation: Any) -> bool:
    if annotation is Path:
        return True
    origin = get_origin(annotation)
    if origin in (Union, Optional):
        return any(_is_path_annotation(arg) for arg in get_args(annotation) if arg is not type(None))
    return False


def _is_bool_annotation(annotation: Any) -> bool:
    if annotation is bool:
        return True
    origin = get_origin(annotation)
    if origin in (Union, Optional):
        return any(_is_bool_annotation(arg) for arg in get_args(annotation) if arg is not type(None))
    return False


__all__ = ["Typer", "Option", "Argument", "Exit", "echo"]
