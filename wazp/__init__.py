from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("wazp")
except PackageNotFoundError:
    # package is not installed
    pass
