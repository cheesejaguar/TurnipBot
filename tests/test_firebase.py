"""
Tests for src/firebase.py
"""
import pytest
from unittest.mock import MagicMock, patch
import json


class TestDumper:
    """Tests for the dumper helper function."""

    def test_dumper_returns_dict(self, fresh_firebase_module):
        """Test that dumper returns __dict__ of an object."""
        class TestObj:
            def __init__(self):
                self.foo = "bar"
                self.num = 42

        obj = TestObj()
        result = fresh_firebase_module.dumper(obj)
        assert result == {"foo": "bar", "num": 42}


class TestIsland:
    """Tests for the Island class."""

    def test_island_init(self, fresh_firebase_module):
        """Test Island initialization with default values."""
        island = fresh_firebase_module.Island("MyIsland")
        assert island.id == "MyIsland"
        assert island.residents == []
        assert island.prices == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert island.purchased == 0
        assert island.purchase_price == 0

    def test_island_repr(self, fresh_firebase_module):
        """Test Island __repr__ returns valid JSON."""
        island = fresh_firebase_module.Island("TestIsland")
        island.residents = ["user1"]
        repr_str = repr(island)
        data = json.loads(repr_str)
        assert data["id"] == "TestIsland"
        assert data["residents"] == ["user1"]

    def test_island_push(self, fresh_firebase_module):
        """Test Island push updates Firebase."""
        island = fresh_firebase_module.Island("TestIsland")
        island.residents = ["user1"]

        mock_doc = MagicMock()
        fresh_firebase_module.island_ref.db.document.return_value = mock_doc

        island.push()

        fresh_firebase_module.island_ref.db.document.assert_called_with("TestIsland")
        mock_doc.update.assert_called_once()

    def test_island_pull(self, fresh_firebase_module):
        """Test Island pull retrieves data from Firebase."""
        mock_doc = MagicMock()
        mock_doc.get.return_value.to_dict.return_value = {
            "id": "TestIsland",
            "residents": ["user1", "user2"],
            "prices": [100, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "purchase_price": 95,
            "purchased": 1
        }
        fresh_firebase_module.island_ref.db.document.return_value = mock_doc

        island = fresh_firebase_module.Island("TestIsland")
        island.pull()

        assert island.residents == ["user1", "user2"]
        assert island.prices[0] == 100
        assert island.prices[1] == 200
        assert island.purchase_price == 95

    def test_island_create(self, fresh_firebase_module):
        """Test Island create adds document to Firebase."""
        mock_doc = MagicMock()
        fresh_firebase_module.island_ref.db.document.return_value = mock_doc

        island = fresh_firebase_module.Island("NewIsland")
        island.create()

        fresh_firebase_module.island_ref.db.document.assert_called_with("NewIsland")
        mock_doc.create.assert_called_once()


class TestDatabaseFunctions:
    """Tests for database helper functions."""

    def test_fetch_islands(self, fresh_firebase_module):
        """Test fetch_islands returns list of island IDs."""
        mock_island1 = MagicMock()
        mock_island1.to_dict.return_value = {"id": "Island1"}
        mock_island2 = MagicMock()
        mock_island2.to_dict.return_value = {"id": "Island2"}

        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_island1, mock_island2]
        fresh_firebase_module.island_ref.db.order_by.return_value = mock_query

        result = fresh_firebase_module.fetch_islands()
        assert result == ["Island1", "Island2"]

    def test_fetch_residents_exists(self, fresh_firebase_module):
        """Test fetch_residents when island exists."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"residents": ["user1", "user2"]}
        fresh_firebase_module.island_ref.db.document.return_value.get.return_value = mock_doc

        result = fresh_firebase_module.fetch_residents("TestIsland")
        assert result == ["user1", "user2"]

    def test_fetch_residents_not_exists(self, fresh_firebase_module):
        """Test fetch_residents when island doesn't exist."""
        mock_doc = MagicMock()
        mock_doc.exists = False
        fresh_firebase_module.island_ref.db.document.return_value.get.return_value = mock_doc

        result = fresh_firebase_module.fetch_residents("NonExistent")
        assert result is None

    def test_fetch_residents_no_residents_key(self, fresh_firebase_module):
        """Test fetch_residents when island has no residents key."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"id": "EmptyIsland"}
        fresh_firebase_module.island_ref.db.document.return_value.get.return_value = mock_doc

        result = fresh_firebase_module.fetch_residents("EmptyIsland")
        assert result == []

    def test_is_registered_true(self, fresh_firebase_module):
        """Test is_registered returns island name when user is registered."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"id": "UserIsland"}
        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_result]
        fresh_firebase_module.island_ref.db.where.return_value = mock_query

        result = fresh_firebase_module.is_registered("TestUser#1234")
        assert result == "UserIsland"

    def test_is_registered_false(self, fresh_firebase_module):
        """Test is_registered returns False when user is not registered."""
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        fresh_firebase_module.island_ref.db.where.return_value = mock_query

        result = fresh_firebase_module.is_registered("UnknownUser#9999")
        assert result is False

    def test_remove_resident_success(self, fresh_firebase_module):
        """Test remove_resident successfully removes user."""
        mock_doc = MagicMock()
        mock_doc.get.return_value.to_dict.return_value = {
            "id": "TestIsland",
            "residents": ["user1", "user2"],
            "prices": [0] * 12,
            "purchase_price": 0,
            "purchased": 0
        }
        fresh_firebase_module.island_ref.db.document.return_value = mock_doc

        result = fresh_firebase_module.remove_resident("user1", "TestIsland")
        assert result is True

    def test_remove_resident_not_found(self, fresh_firebase_module):
        """Test remove_resident returns False when user not in island."""
        mock_doc = MagicMock()
        mock_doc.get.return_value.to_dict.return_value = {
            "id": "TestIsland",
            "residents": ["other_user"],
            "prices": [0] * 12,
            "purchase_price": 0,
            "purchased": 0
        }
        fresh_firebase_module.island_ref.db.document.return_value = mock_doc

        result = fresh_firebase_module.remove_resident("nonexistent_user", "TestIsland")
        assert result is False

    def test_island_exists_true(self, fresh_firebase_module):
        """Test island_exists returns True when island exists."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        fresh_firebase_module.island_ref.db.document.return_value.get.return_value = mock_doc

        result = fresh_firebase_module.island_exists("ExistingIsland")
        assert result is True

    def test_island_exists_false(self, fresh_firebase_module):
        """Test island_exists returns False when island doesn't exist."""
        mock_doc = MagicMock()
        mock_doc.exists = False
        fresh_firebase_module.island_ref.db.document.return_value.get.return_value = mock_doc

        result = fresh_firebase_module.island_exists("NonExistentIsland")
        assert result is False

    def test_find_home_island_found(self, fresh_firebase_module):
        """Test find_home_island returns island name when user found."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"id": "HomeIsland"}
        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_result]
        fresh_firebase_module.island_ref.db.where.return_value = mock_query

        result = fresh_firebase_module.find_home_island("TestUser#1234")
        assert result == "HomeIsland"
        fresh_firebase_module.island_ref.db.where.assert_called_with(
            "residents", "array_contains", "TestUser#1234"
        )

    def test_find_home_island_not_found(self, fresh_firebase_module):
        """Test find_home_island returns None when user not found."""
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        fresh_firebase_module.island_ref.db.where.return_value = mock_query

        result = fresh_firebase_module.find_home_island("UnknownUser")
        assert result is None

    def test_highest_price_with_prices(self, fresh_firebase_module):
        """Test highest_price returns best price and user."""
        mock_island1 = MagicMock()
        mock_island1.to_dict.return_value = {
            "residents": ["user1"],
            "prices": [100, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        mock_island2 = MagicMock()
        mock_island2.to_dict.return_value = {
            "residents": ["user2"],
            "prices": [200, 180, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }

        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_island1, mock_island2]
        fresh_firebase_module.island_ref.db.order_by.return_value = mock_query

        result = fresh_firebase_module.highest_price(0)  # Mon AM slot
        assert result == ("user2", 200)

    def test_highest_price_no_prices(self, fresh_firebase_module):
        """Test highest_price returns None when no prices recorded."""
        mock_island = MagicMock()
        mock_island.to_dict.return_value = {
            "residents": ["user1"],
            "prices": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }

        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_island]
        fresh_firebase_module.island_ref.db.order_by.return_value = mock_query

        result = fresh_firebase_module.highest_price(0)
        assert result is None

    def test_highest_price_no_residents(self, fresh_firebase_module):
        """Test highest_price skips islands with no residents."""
        mock_island = MagicMock()
        mock_island.to_dict.return_value = {
            "residents": [],
            "prices": [500, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }

        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_island]
        fresh_firebase_module.island_ref.db.order_by.return_value = mock_query

        result = fresh_firebase_module.highest_price(0)
        assert result is None

    def test_highest_price_short_prices_array(self, fresh_firebase_module):
        """Test highest_price skips islands with incomplete prices array."""
        mock_island = MagicMock()
        mock_island.to_dict.return_value = {
            "residents": ["user1"],
            "prices": [100, 200]  # Only 2 prices, trying slot 5
        }

        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_island]
        fresh_firebase_module.island_ref.db.order_by.return_value = mock_query

        result = fresh_firebase_module.highest_price(5)  # Wed PM slot
        assert result is None

    def test_highest_price_empty_database(self, fresh_firebase_module):
        """Test highest_price returns None with empty database."""
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        fresh_firebase_module.island_ref.db.order_by.return_value = mock_query

        result = fresh_firebase_module.highest_price(0)
        assert result is None
