class FriendlyCICDHelperError(Exception):
    """Base exception for the application."""
    pass

class APIError(FriendlyCICDHelperError):
    """Raised for issues related to external API calls."""
    pass

class ConfigurationError(FriendlyCICDHelperError):
    """Raised for configuration-related errors."""
    pass

class AnalysisError(FriendlyCICDHelperError):
    """Raised for errors during code analysis."""
    pass