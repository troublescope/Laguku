from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any, Dict
from enum import Enum

class ProviderType(str, Enum):
    AUTO = "auto"
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    AMAZON = "amazon"
    TIDAL = "tidal"
    QOBUZ = "qobuz"
    GENERIC = "generic"

@dataclass
class LagukuConfig:
    """
    Centralized configuration for the Laguku SDK.
    """
    quality: str = "320" # '128', '320', 'lossless'
    provider: ProviderType = ProviderType.AUTO
    preferred_providers: List[ProviderType] = field(default_factory=lambda: [
        ProviderType.QOBUZ,
        ProviderType.TIDAL,
        ProviderType.AMAZON
    ])
    lyric: bool = True
    cover: bool = True
    output_dir: str = "downloads"
    filename_format: str = "{title} - {artist}"
    concurrency: int = 3
    
    # Credentials
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None

    def merge(self, **overrides) -> "LagukuConfig":
        """
        Creates a new config object by merging current values with overrides.
        """
        current_data = asdict(self)
        
        # Special handling for provider enum if passed as string in overrides
        if "provider" in overrides and isinstance(overrides["provider"], str):
            try:
                overrides["provider"] = ProviderType(overrides["provider"].lower())
            except ValueError:
                pass

        clean_overrides = {k: v for k, v in overrides.items() if v is not None and k in current_data}
        return LagukuConfig(**{**current_data, **clean_overrides})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LagukuConfig":
        """
        Creates a LagukuConfig from a dictionary, filtering out extra keys.
        """
        if not data:
            return cls()
        
        # Handle ProviderType enum conversion if passed as string
        if "provider" in data and isinstance(data["provider"], str):
            try:
                data["provider"] = ProviderType(data["provider"].lower())
            except ValueError:
                pass
        
        # Handle preferred_providers list conversion
        if "preferred_providers" in data and isinstance(data["preferred_providers"], list):
            new_list = []
            for p in data["preferred_providers"]:
                if isinstance(p, str):
                    try:
                        new_list.append(ProviderType(p.lower()))
                    except ValueError:
                        continue
                else:
                    new_list.append(p)
            data["preferred_providers"] = new_list
                
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in valid_keys})
