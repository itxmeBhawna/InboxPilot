"""Custom exceptions for the InboxAgent AI reasoning engine."""


class InboxAgentError(Exception):
    """Base exception for all InboxAgent errors."""

    pass


class InvalidAgentOutputError(InboxAgentError):
    """Raised when Gemini returns malformed, unparseable, or schema-invalid JSON."""

    def __init__(self, message: str, raw_output: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.raw_output = raw_output

    def __str__(self) -> str:
        if self.raw_output:
            return f"{self.message} | Raw Output: {self.raw_output[:200]}..."
        return self.message
