import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class FileOperation:
    root_dir: str
    _root_path: Path = field(init=False, repr=False)

    def __post_init__(self):
        """Initialize the root path."""
        self._root_path = Path(self.root_dir)
        if not self._root_path.exists():
            raise Exception(f"Path does not exist: {self.root_dir}")
        if not self._root_path.is_dir():
            raise Exception(f"Path is neither a file nor a directory: {self.root_dir}")

    def _validate_path_in_root(self, path: str) -> str:
        """Check if the given path is within the root directory."""
        abs_path = self.get_absolute_path(path)
        if self._root_path.as_posix() not in abs_path.as_posix():
            raise ValueError(f"Path is not within the root directory: {path}")
        return abs_path.as_posix()

    @property
    def docstring(self) -> str:
        """Return the docstring of the class."""
        return self.__call__.__doc__ or "No docstring provided"

    @abc.abstractmethod
    def __call__(
        self,
        *args: Optional[Tuple],
        **kwargs: Optional[dict],
    ) -> Dict[str, Any]:
        """Perform the file operation and return the result."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the operation."""

    def get_absolute_path(self, path: str) -> Path:
        """Get the absolute path of the given path."""
        return self._root_path / path
