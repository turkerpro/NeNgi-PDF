"""
Result pattern for standardized error handling across NeNgi-PDF core modules.
Replaces scattered bool/None/Exception returns with a unified Result[T] type.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class Result(Generic[T]):
    """Standardized result container for all core operations."""
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    hint: Optional[str] = None
    error_code: Optional[str] = None

    @staticmethod
    def ok(value: T) -> "Result[T]":
        return Result(success=True, value=value)

    @staticmethod
    def fail(error: str, hint: Optional[str] = None, error_code: Optional[str] = None) -> "Result[T]":
        return Result(success=False, error=error, hint=hint, error_code=error_code)

    @staticmethod
    def from_exception(exc: Exception, hint: Optional[str] = None, error_code: Optional[str] = None) -> "Result[T]":
        """Convert an exception to a failed Result with context."""
        error_msg = str(exc)
        if not error_msg:
            error_msg = f"{type(exc).__name__}"
        return Result(
            success=False,
            error=error_msg,
            hint=hint,
            error_code=error_code or type(exc).__name__
        )

    def __bool__(self) -> bool:
        return self.success

    def unwrap(self) -> T:
        """Return value or raise RuntimeError with error context."""
        if not self.success:
            raise RuntimeError(f"Result unwrap failed: {self.error} (code: {self.error_code})")
        return self.value  # type: ignore

    def unwrap_or(self, default: T) -> T:
        return self.value if self.success else default

    def map(self, fn) -> "Result":
        """Transform value if success, propagate failure."""
        if not self.success:
            return Result(success=False, error=self.error, hint=self.hint, error_code=self.error_code)
        try:
            return Result.ok(fn(self.value))
        except Exception as exc:
            return Result.from_exception(exc, hint="map transformation failed")

    def map_err(self, fn) -> "Result":
        """Transform error if failure, propagate success."""
        if self.success:
            return self
        try:
            return Result(success=False, error=fn(self.error), hint=self.hint, error_code=self.error_code)
        except Exception as exc:
            return Result.from_exception(exc, hint="map_err transformation failed")