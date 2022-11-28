from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("wazp")
except PackageNotFoundError:
    # package is not installed
    pass