import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PromptEvaluationException(Exception):
    """Base exception for all prompt evaluation errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        is_user_error: bool = False
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.is_user_error = is_user_error

        # Log the error
        log_level = logging.WARNING if is_user_error else logging.ERROR
        logger.log(log_level, f"[{error_code}] {message}", extra={"details": self.details})

        super().__init__(self.message)


class ValidationException(PromptEvaluationException):
    """Raised when validation of input data fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            is_user_error=True
        )


class LLMException(PromptEvaluationException):
    """Raised when LLM API call fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            details=details,
            is_user_error=False
        )


class DatasetGenerationException(PromptEvaluationException):
    """Raised when synthetic dataset generation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATASET_GENERATION_ERROR",
            details=details,
            is_user_error=False
        )


class AnalysisException(PromptEvaluationException):
    """Raised when prompt analysis fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details=details,
            is_user_error=False
        )


class EvaluationException(PromptEvaluationException):
    """Raised when evaluation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="EVALUATION_ERROR",
            details=details,
            is_user_error=False
        )


def format_error_response(exc: PromptEvaluationException) -> Dict[str, Any]:
    """Format exception as API response."""
    return {
        "error": exc.message,
        "error_code": exc.error_code,
        "details": exc.details,
        "type": "user_error" if exc.is_user_error else "system_error"
    }
