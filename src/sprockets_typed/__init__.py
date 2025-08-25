from importlib import metadata

version = metadata.version('sprockets-typed')
version_info: list[int | str] = [int(c) for c in version.split('.')[:3]]
version_info.extend(version.split('.')[3:])

__all__ = [
    'version',
    'version_info',
]
