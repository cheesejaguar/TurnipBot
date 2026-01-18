"""
Pytest configuration and fixtures for TurnipBot tests.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os


def pytest_configure(config):
    """Configure pytest and set up mocks before any tests run."""
    # Set environment variables before any imports
    os.environ['DISCORD_TOKEN'] = 'test_token'
    os.environ['FIREBASE_JSON'] = '{"type": "service_account", "project_id": "test"}'


@pytest.fixture(scope="session", autouse=True)
def mock_external_dependencies():
    """Mock all external dependencies at session level."""
    # Create mock Firebase modules
    mock_credentials = MagicMock()
    mock_firestore = MagicMock()
    mock_firebase_admin = MagicMock()
    mock_firebase_admin.credentials = mock_credentials
    mock_firebase_admin.firestore = mock_firestore

    # Create mock Discord modules
    mock_discord = MagicMock()
    mock_commands = MagicMock()
    mock_bot_instance = MagicMock()
    mock_commands.Bot.return_value = mock_bot_instance

    # Patch sys.modules before anything imports these
    with patch.dict(sys.modules, {
        'firebase_admin': mock_firebase_admin,
        'firebase_admin.credentials': mock_credentials,
        'firebase_admin.firestore': mock_firestore,
        'discord': mock_discord,
        'discord.ext': MagicMock(),
        'discord.ext.commands': mock_commands,
    }):
        yield


@pytest.fixture
def mock_ctx():
    """Create a mock Discord context object."""
    ctx = MagicMock()
    ctx.message.author = MagicMock()
    ctx.message.author.__str__ = MagicMock(return_value="TestUser#1234")
    ctx.message.author.mention = "@TestUser"
    ctx.message.guild.get_member_named = MagicMock(return_value=None)
    ctx.send = MagicMock()
    return ctx


@pytest.fixture
def mock_ctx_with_member():
    """Create a mock Discord context with guild member lookup working."""
    ctx = MagicMock()
    ctx.message.author = MagicMock()
    ctx.message.author.__str__ = MagicMock(return_value="TestUser#1234")
    ctx.message.author.mention = "@TestUser"

    mock_member = MagicMock()
    mock_member.mention = "@FoundUser"
    ctx.message.guild.get_member_named = MagicMock(return_value=mock_member)
    ctx.send = MagicMock()
    return ctx


@pytest.fixture
def fresh_bot_module():
    """Get a fresh import of the bot module with mocked dependencies."""
    # Clear cached modules
    modules_to_clear = [key for key in sys.modules.keys() if key.startswith('src.')]
    for mod in modules_to_clear:
        del sys.modules[mod]

    # Now import fresh
    import src.bot
    return src.bot


@pytest.fixture
def fresh_firebase_module():
    """Get a fresh import of the firebase module with mocked dependencies."""
    # Clear cached modules
    modules_to_clear = [key for key in sys.modules.keys() if key.startswith('src.')]
    for mod in modules_to_clear:
        del sys.modules[mod]

    # Now import fresh
    import src.firebase
    return src.firebase
