class LagukuError(Exception):
    """Base exception for lagukuSDK"""

class ProviderError(LagukuError):
    """Raised when a provider fails"""

class DownloadError(LagukuError):
    """Raised when a download fails"""

class ResolutionError(LagukuError):
    """Raised when stream resolution fails"""

class TaggingError(LagukuError):
    """Raised when metadata embedding fails"""

class RateLimitError(ProviderError):
    """Raised when hitting provider rate limits"""

class DecryptionError(LagukuError):
    """Raised when media decryption fails"""
