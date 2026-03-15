from typing import Dict, Type, TYPE_CHECKING
from laguku.config import ProviderType

if TYPE_CHECKING:
    from laguku.providers.base import BaseProvider

class ProviderRegistry:
    """
    Registry for music providers to allow dynamic discovery.
    """
    _providers: Dict[ProviderType, Type["BaseProvider"]] = {}

    @classmethod
    def register(cls, provider_type: ProviderType):
        def decorator(provider_cls: Type["BaseProvider"]):
            cls._providers[provider_type] = provider_cls
            return provider_cls
        return decorator

    @classmethod
    def get_provider_class(cls, provider_type: ProviderType) -> Type["BaseProvider"]:
        provider_cls = cls._providers.get(provider_type)
        if not provider_cls:
            # Fallback for string matches if Enum conversion failed
            if isinstance(provider_type, str):
                for pt, pcls in cls._providers.items():
                    if pt.value == provider_type:
                        return pcls
        return provider_cls

    @classmethod
    def list_available(cls):
        return list(cls._providers.keys())
