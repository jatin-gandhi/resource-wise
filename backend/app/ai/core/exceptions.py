"""AI system exceptions."""


class AIError(Exception):
    """Base exception for AI system errors."""

    pass


class ConfigurationError(AIError):
    """Configuration related errors."""

    pass


class AgentError(AIError):
    """Agent processing errors."""

    pass


class WorkflowError(AIError):
    """Workflow execution errors."""

    pass


class ContextError(AIError):
    """Context management errors."""

    pass


class StreamError(AIError):
    """Streaming related errors."""

    pass
