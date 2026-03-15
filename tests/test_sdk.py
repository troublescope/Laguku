import unittest
from laguku import Laguku, LagukuConfig, ProviderType

class TestLagukuConfig(unittest.TestCase):
    def test_config_initialization(self):
        config = LagukuConfig(quality="320", provider=ProviderType.AMAZON)
        self.assertEqual(config.quality, "320")
        self.assertEqual(config.provider, ProviderType.AMAZON)

    def test_config_merge(self):
        base_config = LagukuConfig(quality="320", provider=ProviderType.AMAZON)
        merged = base_config.merge(quality="lossless", provider=ProviderType.QOBUZ)
        
        # Base config should not change
        self.assertEqual(base_config.quality, "320")
        self.assertEqual(base_config.provider, ProviderType.AMAZON)
        
        # Merged config should have new values
        self.assertEqual(merged.quality, "lossless")
        self.assertEqual(merged.provider, ProviderType.QOBUZ)

    def test_config_merge_partial(self):
        base_config = LagukuConfig(quality="320", provider=ProviderType.AMAZON, lyric=True)
        merged = base_config.merge(quality="lossless")
        
        self.assertEqual(merged.quality, "lossless")
        self.assertEqual(merged.provider, ProviderType.AMAZON)
        self.assertEqual(merged.lyric, True)

    def test_auto_provider_default(self):
        config = LagukuConfig()
        self.assertEqual(config.provider, ProviderType.AUTO)
        self.assertIn(ProviderType.QOBUZ, config.preferred_providers)

    def test_preferred_providers_override(self):
        config = LagukuConfig(preferred_providers=["amazon", "tidal"])
        self.assertEqual(len(config.preferred_providers), 2)
        self.assertEqual(config.preferred_providers[0], ProviderType.AMAZON)
        self.assertEqual(config.preferred_providers[1], ProviderType.TIDAL)

class TestLagukuClient(unittest.TestCase):
    def test_sdk_init(self):
        sdk = Laguku(quality="320", provider="amazon")
        self.assertEqual(sdk._async_sdk.config.quality, "320")
        self.assertEqual(sdk._async_sdk.config.provider, ProviderType.AMAZON)

if __name__ == '__main__':
    unittest.main()
