"""Validation and preview tools for the Image-to-PPTX IR specification."""

from .validator import Issue, ValidationResult, validate_document

__all__ = ["Issue", "ValidationResult", "validate_document"]
__version__ = "0.1.0"
