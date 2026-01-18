"""
Tests for src/settings.py
"""
import pytest
from unittest.mock import patch, MagicMock
import os
import sys


class TestSettings:
    """Tests for settings module."""

    def test_settings_loads_discord_token(self):
        """Test that DISCORD_TOKEN is loaded from environment."""
        # Clear cached modules
        modules_to_clear = [key for key in sys.modules.keys() if key.startswith('src.')]
        for mod in modules_to_clear:
            del sys.modules[mod]

        with patch.dict(os.environ, {
            'DISCORD_TOKEN': 'test_discord_token_123',
            'FIREBASE_JSON': '{"type": "service_account", "project_id": "test"}'
        }):
            from src.settings import TOKEN
            assert TOKEN == 'test_discord_token_123'

    def test_settings_loads_firebase_json(self):
        """Test that FIREBASE_JSON is loaded and parsed."""
        modules_to_clear = [key for key in sys.modules.keys() if key.startswith('src.')]
        for mod in modules_to_clear:
            del sys.modules[mod]

        with patch.dict(os.environ, {
            'DISCORD_TOKEN': 'test_token',
            'FIREBASE_JSON': "{'type': 'service_account', 'project_id': 'test-project'}"
        }):
            from src.settings import KEY_CONTENTS
            assert KEY_CONTENTS['type'] == 'service_account'
            assert KEY_CONTENTS['project_id'] == 'test-project'

    def test_settings_parses_single_quotes_in_firebase_json(self):
        """Test that single quotes in FIREBASE_JSON are converted to double quotes."""
        modules_to_clear = [key for key in sys.modules.keys() if key.startswith('src.')]
        for mod in modules_to_clear:
            del sys.modules[mod]

        with patch.dict(os.environ, {
            'DISCORD_TOKEN': 'test_token',
            'FIREBASE_JSON': "{'key': 'value', 'nested': {'inner': 'data'}}"
        }):
            from src.settings import KEY_CONTENTS
            assert KEY_CONTENTS['key'] == 'value'
            assert KEY_CONTENTS['nested']['inner'] == 'data'
