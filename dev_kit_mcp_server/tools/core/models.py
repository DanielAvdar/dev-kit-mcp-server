"""Base models for tool parameters.

This module provides base Pydantic models for tool parameters.
"""

from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel, create_model

# Type variable for the model
ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseToolParams(BaseModel):
    """Base class for tool parameters.

    This class provides a foundation for all tool parameter models.
    """

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        extra = "forbid"


class ToolModelMixin(Generic[ModelT]):
    """Mixin for tool classes that use Pydantic models.

    This mixin provides functionality for working with Pydantic models
    in tool classes.
    """

    # Class variable to store the model class
    model_class: Type[ModelT]

    @classmethod
    def create_model(cls, name: str, **field_definitions: Any) -> Type[BaseToolParams]:
        """Create a Pydantic model for the tool parameters.

        Args:
            name: The name of the model
            **field_definitions: Field definitions for the model

        Returns:
            A Pydantic model class for the tool parameters

        """
        return create_model(
            name,
            __base__=BaseToolParams,
            **field_definitions,
        )
