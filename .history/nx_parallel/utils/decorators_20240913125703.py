import os
import networkx as nx
from dataclasses import asdict
from typing import Callable, Any, TypeVar, cast
from functools import wraps
from joblib import parallel_config


__all__ = ["_configure_if_nx_active"]

F = TypeVar("F", bound=Callable[..., Any])


def _configure_if_nx_active() -> Callable[[F], F]:
    """
    Decorator to set the configuration for the parallel computation
    of the nx-parallel algorithms.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if (
                nx.config.backends.parallel.active
                or "PYTEST_CURRENT_TEST" in os.environ
            ):
                # Activate nx config system in nx_parallel with:
                # `nx.config.backends.parallel.active = True`
                config_dict = asdict(nx.config.backends.parallel)
                config_dict.update(config_dict.pop("backend_params"))
                config_dict.pop("active", None)
                with parallel_config(**config_dict):
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
