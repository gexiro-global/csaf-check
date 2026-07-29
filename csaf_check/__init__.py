"""csaf-check - validate CSAF 2.0 documents from Python using the BSI validator library."""

from .validator import ValidationResult, node_available, validator_available, validate

__version__ = "0.1.0"
__all__ = ["ValidationResult", "node_available", "validator_available", "validate"]
