"""Global parameter accessor used by GUI apps.

This module holds a provider (set by `MasterGui`) which implements
`get_parameter(key, cast=int, default=None)`. Callers can import
`parameters.get_parameter` safely; it will return `default` until the
provider is registered at runtime.
"""

_provider = None


def set_provider(provider):
    """Register an object that exposes `get_parameter(key, cast, default)`.

    The provider is typically the running `MasterGui` instance.
    """
    global _provider
    _provider = provider


def get_parameter(key, cast=int, default=None):
    """Global accessor delegating to the registered provider.

    Returns `default` if no provider is registered or conversion fails.
    """
    try:
        if _provider is None:
            return default
        getter = getattr(_provider, "get_parameter", None)
        if callable(getter):
            return getter(key, cast=cast, default=default)
        # Fallback: try direct dict access
        params = getattr(_provider, "parameters", None)
        if params is None:
            return default
        val = params.get(key)
        if val is None:
            return default
        if cast is None:
            return val
        try:
            return cast(val)
        except Exception:
            return default
    except Exception:
        return default
