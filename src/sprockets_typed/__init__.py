from importlib import metadata

from sprockets_typed.api import TypedRequestHandler
from sprockets_typed.exceptions import RequestValidationError

version = metadata.version('sprockets-typed')
version_info: list[int | str] = [int(c) for c in version.split('.')[:3]]
version_info.extend(version.split('.')[3:])

__all__ = [
    'RequestValidationError',
    'TypedRequestHandler',
    'version',
    'version_info',
]
