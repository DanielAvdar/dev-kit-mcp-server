import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

@dataclass
class _Operation:
    root_dir: str
    _root_path: Path = field(init=False, repr=False)

    def __post_init__(self):
        """Initialize the root path."""
        self._root_path = Path(self.root_dir)
        if not self._root_path.exists():
            raise Exception(f"Path does not exist: {self.root_dir}")
        if not self._root_path.is_dir():
            raise Exception(f"Path is neither a file nor a directory: {self.root_dir}")

    @property
    def docstring(self) -> str:
        """Return the docstring of the class."""
        return self.__call__.__doc__ or "No docstring provided"

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the operation."""

    @classmethod
    def get_absolute_path(cls, root_path: Path, path: str) -> Path:
        """Get the absolute path of the given path."""
        if Path(path).is_absolute():
            return Path(path).resolve()
        return Path(root_path.as_posix() + path).resolve()

    @classmethod
    def _validate_path_in_root(cls, root_dir: Path, path: str) -> str:
        """Check if the given path is within the root directory."""
        root_path = root_dir
        abs_path = cls.get_absolute_path(root_path, path)
        if root_path.as_posix() not in abs_path.as_posix():
            raise ValueError(f"Path is not within the root directory: {root_path.as_posix()}")
        return abs_path.as_posix()

@dataclass
class FileOperation(_Operation):


    @abc.abstractmethod
    def __call__(
        self,
        *args: Optional[Tuple],
        **kwargs: Optional[dict],
    ) -> Dict[str, Any]:
        """Perform the file operation and return the result."""


@dataclass
class AsyncOperation(_Operation):
    @abc.abstractmethod
    async def __call__(
        self,
        *args: Optional[Tuple],
        **kwargs: Optional[dict],
    ) -> Dict[str, Any]:
        """Perform the file operation and return the result."""
