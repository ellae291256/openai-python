from __future__ import annotations

import inspect
from typing import Any, Callable


def function_has_argument(func: Callable[..., Any], arg_name: str) -> bool:
    """Returns whether or not the given function has a specific parameter"""
    sig = inspect.signature(func)
    return arg_name in sig.parameters


def assert_signatures_in_sync(
    source_func: Callable[..., Any],
    check_func: Callable[..., Any],
    *,
    exclude_params: set[str] = set(),
    description: str = "",
) -> None:
    """Ensure that the signature of the second function matches the first."""

    check_sig = inspect.signature(check_func)
    source_sig = inspect.signature(source_func)

    errors: list[str] = []

    for name, source_param in source_sig.parameters.items():
        if name in exclude_params:
            continue

        custom_param = check_sig.parameters.get(name)
        if not custom_param:
            errors.append(f"the `{name}` param is missing")
            continue

        if not _annotations_are_equivalent(custom_param.annotation, source_param.annotation):
            errors.append(
                f"types for the `{name}` param are do not match; source={repr(source_param.annotation)} checking={repr(custom_param.annotation)}"
            )
            continue

    if errors:
        raise AssertionError(
            f"{len(errors)} errors encountered when comparing signatures{description}:\n\n" + "\n\n".join(errors)
        )


def _annotations_are_equivalent(a: Any, b: Any) -> bool:
    """Check if two annotations are semantically equivalent."""
    if a is b:
        return True
    if a is None or b is None:
        return a is b
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if isinstance(a, type) and isinstance(b, type):
        return a is b
    if isinstance(a, typing._GenericAlias) and isinstance(b, typing._GenericAlias):
        return _generic_alias_equivalent(a, b)
    if isinstance(a, typing._SpecialForm) and isinstance(b, typing._SpecialForm):
        return a is b
    return False


def _generic_alias_equivalent(a: Any, b: Any) -> bool:
    """Check if two generic aliases are semantically equivalent."""
    if a.origin is not b.origin:
        return False
    if a.args is None and b.args is None:
        return True
    if a.args is None or b.args is None:
        return False
    if len(a.args) != len(b.args):
        return False
    for arg_a, arg_b in zip(a.args, b.args):
        if not _annotations_are_equivalent(arg_a, arg_b):
            return False
    return True
