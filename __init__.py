from contextlib import suppress
import importlib.metadata
from pathlib import Path
from SpotifyUtil.SpotifyUtil import SpotifyUtil
from SpotifyUtil.config import Config


def extract_version() -> str:
    """Returns either the version of installed package or the one
    found in nearby pyproject.toml"""
    with suppress(FileNotFoundError, StopIteration):
        with open((root_dir := Path(__file__).parent.parent)
                / "pyproject.toml", encoding="utf-8") as pyproject_toml:
            version = (
                next(line for line in pyproject_toml if line.startswith("version"))
                .split("=")[1]
                .strip("'\"\n ")
            )
            return f"{version}-dev (at {root_dir})"
    return importlib.metadata.version(__package__ or __name__.split(".", maxsplit=1)[0])

__version__ = extract_version()

__all__ = [
    "Config",
    "SpotifyUtil",
]