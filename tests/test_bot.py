"""
Tests for src/bot.py
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import time


class TestGetCurrentSlot:
    """Tests for get_current_slot function."""

    def test_sunday_returns_sunday(self, fresh_bot_module):
        """Test that Sunday returns 'Sunday'."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 6  # Sunday
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Sunday"

    def test_monday_am_slot(self, fresh_bot_module):
        """Test Monday AM slot (8am-12pm)."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(10, 0)  # 10am
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Mon AM"

    def test_tuesday_pm_slot(self, fresh_bot_module):
        """Test Tuesday PM slot (12pm-10pm)."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.time.return_value = time(14, 0)  # 2pm
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Tue PM"

    def test_wednesday_am_slot(self, fresh_bot_module):
        """Test Wednesday AM slot."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 2  # Wednesday
            mock_now.time.return_value = time(8, 30)
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Wed AM"

    def test_thursday_pm_slot(self, fresh_bot_module):
        """Test Thursday PM slot."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 3  # Thursday
            mock_now.time.return_value = time(18, 0)
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Thu PM"

    def test_friday_am_slot(self, fresh_bot_module):
        """Test Friday AM slot."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 4  # Friday
            mock_now.time.return_value = time(11, 30)
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Fri AM"

    def test_saturday_pm_slot(self, fresh_bot_module):
        """Test Saturday PM slot."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 5  # Saturday
            mock_now.time.return_value = time(20, 0)
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result == "Sat PM"

    def test_closed_early_morning(self, fresh_bot_module):
        """Test that early morning (before 8am) returns False."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 0  # Monday
            mock_now.time.return_value = time(6, 0)  # 6am - closed
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result is False

    def test_closed_late_night(self, fresh_bot_module):
        """Test that late night (after 10pm) returns False."""
        with patch.object(fresh_bot_module, 'datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.weekday.return_value = 2  # Wednesday
            mock_now.time.return_value = time(23, 0)  # 11pm - closed
            mock_datetime.now.return_value = mock_now

            result = fresh_bot_module.get_current_slot()
            assert result is False


class TestValidatePrice:
    """Tests for validate_price function."""

    def test_valid_price(self, fresh_bot_module):
        """Test valid price returns price and no error."""
        price, error = fresh_bot_module.validate_price(100)
        assert price == 100
        assert error is None

    def test_valid_price_string(self, fresh_bot_module):
        """Test valid price as string."""
        price, error = fresh_bot_module.validate_price("150")
        assert price == 150
        assert error is None

    def test_price_too_low(self, fresh_bot_module):
        """Test price below 1 returns error."""
        price, error = fresh_bot_module.validate_price(0)
        assert price is None
        assert error == "Price must be at least 1 bell."

    def test_price_negative(self, fresh_bot_module):
        """Test negative price returns error."""
        price, error = fresh_bot_module.validate_price(-50)
        assert price is None
        assert error == "Price must be at least 1 bell."

    def test_price_too_high(self, fresh_bot_module):
        """Test price above 999 returns error."""
        price, error = fresh_bot_module.validate_price(1000)
        assert price is None
        assert error == "Price seems too high. Maximum is 999 bells."

    def test_price_invalid_string(self, fresh_bot_module):
        """Test invalid string returns error."""
        price, error = fresh_bot_module.validate_price("abc")
        assert price is None
        assert error == "Invalid price. Please enter a number."

    def test_price_none(self, fresh_bot_module):
        """Test None value returns error."""
        price, error = fresh_bot_module.validate_price(None)
        assert price is None
        assert error == "Invalid price. Please enter a number."

    def test_price_boundary_low(self, fresh_bot_module):
        """Test minimum valid price (1)."""
        price, error = fresh_bot_module.validate_price(1)
        assert price == 1
        assert error is None

    def test_price_boundary_high(self, fresh_bot_module):
        """Test maximum valid price (999)."""
        price, error = fresh_bot_module.validate_price(999)
        assert price == 999
        assert error is None


class TestRegisterResident:
    """Tests for register_resident function."""

    def test_register_empty_island_name(self, fresh_bot_module, mock_ctx):
        """Test registration with empty island name."""
        result = fresh_bot_module.register_resident(mock_ctx, "")
        assert "Please provide an island name" in result

    def test_register_whitespace_island_name(self, fresh_bot_module, mock_ctx):
        """Test registration with whitespace-only island name."""
        result = fresh_bot_module.register_resident(mock_ctx, "   ")
        assert "Please provide an island name" in result

    def test_register_none_island_name(self, fresh_bot_module, mock_ctx):
        """Test registration with None island name."""
        result = fresh_bot_module.register_resident(mock_ctx, None)
        assert "Please provide an island name" in result

    def test_register_already_registered(self, fresh_bot_module, mock_ctx):
        """Test registration when user is already registered."""
        with patch.object(fresh_bot_module, 'is_registered', return_value="ExistingIsland"):
            result = fresh_bot_module.register_resident(mock_ctx, "NewIsland")
            assert "already registered" in result

    def test_register_new_island(self, fresh_bot_module, mock_ctx):
        """Test registration to new island."""
        mock_island = MagicMock()
        mock_island.residents = []

        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            with patch.object(fresh_bot_module, 'island_exists', return_value=False):
                with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                    result = fresh_bot_module.register_resident(mock_ctx, "NewIsland")
                    assert "now registered" in result
                    mock_island.create.assert_called_once()

    def test_register_existing_island(self, fresh_bot_module, mock_ctx):
        """Test registration to existing island."""
        mock_island = MagicMock()
        mock_island.residents = []

        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            with patch.object(fresh_bot_module, 'island_exists', return_value=True):
                with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                    result = fresh_bot_module.register_resident(mock_ctx, "ExistingIsland")
                    assert "now registered" in result
                    mock_island.pull.assert_called_once()
                    mock_island.create.assert_not_called()

    def test_register_exception_handling(self, fresh_bot_module, mock_ctx):
        """Test registration error handling."""
        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            with patch.object(fresh_bot_module, 'island_exists', side_effect=Exception("DB Error")):
                result = fresh_bot_module.register_resident(mock_ctx, "TestIsland")
                assert "Registration error" in result


class TestUnregisterResident:
    """Tests for unregister_resident function."""

    def test_unregister_not_registered(self, fresh_bot_module, mock_ctx):
        """Test unregister when user is not registered."""
        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            result = fresh_bot_module.unregister_resident(mock_ctx)
            assert "not registered" in result

    def test_unregister_success(self, fresh_bot_module, mock_ctx):
        """Test successful unregistration."""
        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'remove_resident', return_value=True):
                result = fresh_bot_module.unregister_resident(mock_ctx)
                assert "unregistered" in result

    def test_unregister_failed(self, fresh_bot_module, mock_ctx):
        """Test failed unregistration (user not in island)."""
        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'remove_resident', return_value=False):
                result = fresh_bot_module.unregister_resident(mock_ctx)
                assert "Could not unregister" in result

    def test_unregister_exception(self, fresh_bot_module, mock_ctx):
        """Test unregistration error handling."""
        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'remove_resident', side_effect=Exception("DB Error")):
                result = fresh_bot_module.unregister_resident(mock_ctx)
                assert "Unregistration error" in result


class TestGetPrices:
    """Tests for get_prices function."""

    def test_get_prices_registered(self, fresh_bot_module):
        """Test get_prices for registered user."""
        mock_island = MagicMock()
        mock_island.prices = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 0]
        mock_island.purchase_price = 95

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.get_prices("User#1234")
                assert "Prices:" in result
                assert "Sunday purchase price: 95 bells" in result

    def test_get_prices_not_registered(self, fresh_bot_module):
        """Test get_prices for unregistered user."""
        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            result = fresh_bot_module.get_prices("Unknown#9999")
            assert "not registered" in result


class TestSetPrice:
    """Tests for set_price function."""

    def test_set_price_not_registered(self, fresh_bot_module, mock_ctx):
        """Test set_price when user is not registered."""
        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            result = fresh_bot_module.set_price(mock_ctx, "100")
            assert "not registered" in result

    def test_set_price_invalid_price(self, fresh_bot_module, mock_ctx):
        """Test set_price with invalid price."""
        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            result = fresh_bot_module.set_price(mock_ctx, "abc")
            assert "Invalid price" in result

    def test_set_price_with_desired_slot_sunday(self, fresh_bot_module, mock_ctx):
        """Test set_price with Sunday slot specified."""
        mock_island = MagicMock()
        mock_island.prices = [0] * 12
        mock_island.purchase_price = 0

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.set_price(mock_ctx, "95", "Sunday")
                assert "set price" in result
                assert mock_island.purchase_price == 95

    def test_set_price_with_desired_slot_weekday(self, fresh_bot_module, mock_ctx):
        """Test set_price with weekday slot specified."""
        mock_island = MagicMock()
        mock_island.prices = [0] * 12

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.set_price(mock_ctx, "150", "Mon AM")
                assert "set price" in result
                assert mock_island.prices[0] == 150

    def test_set_price_with_invalid_slot(self, fresh_bot_module, mock_ctx):
        """Test set_price with invalid time slot."""
        mock_island = MagicMock()
        mock_island.prices = [0] * 12

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.set_price(mock_ctx, "100", "Invalid Slot")
                assert "Invalid time slot" in result

    def test_set_price_auto_slot_sunday(self, fresh_bot_module, mock_ctx):
        """Test set_price with auto slot detection on Sunday."""
        mock_island = MagicMock()
        mock_island.prices = [0] * 12
        mock_island.purchase_price = 0

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                with patch.object(fresh_bot_module, 'get_current_slot', return_value="Sunday"):
                    result = fresh_bot_module.set_price(mock_ctx, "95")
                    assert "Sunday purchase price" in result

    def test_set_price_auto_slot_weekday(self, fresh_bot_module, mock_ctx):
        """Test set_price with auto slot detection on weekday."""
        mock_island = MagicMock()
        mock_island.prices = [0] * 12

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                with patch.object(fresh_bot_module, 'get_current_slot', return_value="Mon AM"):
                    result = fresh_bot_module.set_price(mock_ctx, "100")
                    assert "set price" in result
                    assert "Mon AM" in result

    def test_set_price_store_closed(self, fresh_bot_module, mock_ctx):
        """Test set_price when store is closed."""
        mock_island = MagicMock()
        mock_island.prices = [0] * 12

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                with patch.object(fresh_bot_module, 'get_current_slot', return_value=False):
                    result = fresh_bot_module.set_price(mock_ctx, "100")
                    assert "closed" in result


class TestBestPrice:
    """Tests for best_price function."""

    def test_best_price_sunday(self, fresh_bot_module, mock_ctx):
        """Test best_price on Sunday."""
        with patch.object(fresh_bot_module, 'get_current_slot', return_value="Sunday"):
            result = fresh_bot_module.best_price(mock_ctx)
            assert "buying day" in result

    def test_best_price_closed(self, fresh_bot_module, mock_ctx):
        """Test best_price when store is closed."""
        with patch.object(fresh_bot_module, 'get_current_slot', return_value=False):
            result = fresh_bot_module.best_price(mock_ctx)
            assert "closed" in result

    def test_best_price_no_prices(self, fresh_bot_module, mock_ctx):
        """Test best_price when no prices recorded."""
        with patch.object(fresh_bot_module, 'get_current_slot', return_value="Mon AM"):
            with patch.object(fresh_bot_module, 'highest_price', return_value=None):
                result = fresh_bot_module.best_price(mock_ctx)
                assert "No prices have been recorded" in result

    def test_best_price_with_discord_user(self, fresh_bot_module, mock_ctx_with_member):
        """Test best_price when Discord user is found."""
        with patch.object(fresh_bot_module, 'get_current_slot', return_value="Mon AM"):
            with patch.object(fresh_bot_module, 'highest_price', return_value=("BestUser#1234", 500)):
                result = fresh_bot_module.best_price(mock_ctx_with_member)
                assert "@FoundUser" in result
                assert "500" in result

    def test_best_price_without_discord_user(self, fresh_bot_module, mock_ctx):
        """Test best_price when Discord user is not found in guild."""
        with patch.object(fresh_bot_module, 'get_current_slot', return_value="Mon AM"):
            with patch.object(fresh_bot_module, 'highest_price', return_value=("OfflineUser#1234", 400)):
                result = fresh_bot_module.best_price(mock_ctx)
                assert "400" in result
                assert "OfflineUser#1234" in result


class TestReturnPredictionUrl:
    """Tests for return_prediction_url function."""

    def test_prediction_url_not_registered(self, fresh_bot_module, mock_ctx):
        """Test prediction URL when user is not registered."""
        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            result = fresh_bot_module.return_prediction_url(mock_ctx)
            assert result is None

    def test_prediction_url_registered(self, fresh_bot_module, mock_ctx):
        """Test prediction URL for registered user."""
        mock_island = MagicMock()
        mock_island.purchase_price = 95
        mock_island.prices = [100, 90, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.return_prediction_url(mock_ctx)
                assert result.startswith("https://turnipprophet.io/?prices=")

    def test_prediction_url_with_zero_purchase_price(self, fresh_bot_module, mock_ctx):
        """Test prediction URL with zero purchase price."""
        mock_island = MagicMock()
        mock_island.purchase_price = 0
        mock_island.prices = [100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.return_prediction_url(mock_ctx)
                assert "=." in result  # 0 at start becomes empty


class TestResetWeekPrices:
    """Tests for reset_week_prices function."""

    def test_reset_week_not_registered(self, fresh_bot_module, mock_ctx):
        """Test reset_week when user is not registered."""
        with patch.object(fresh_bot_module, 'is_registered', return_value=False):
            result = fresh_bot_module.reset_week_prices(mock_ctx)
            assert "not registered" in result

    def test_reset_week_success(self, fresh_bot_module, mock_ctx):
        """Test successful week reset."""
        mock_island = MagicMock()
        mock_island.prices = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 0]
        mock_island.purchase_price = 95

        with patch.object(fresh_bot_module, 'is_registered', return_value="TestIsland"):
            with patch.object(fresh_bot_module, 'Island', return_value=mock_island):
                result = fresh_bot_module.reset_week_prices(mock_ctx)
                assert "reset all turnip prices" in result
                assert mock_island.prices == [0] * 12
                assert mock_island.purchase_price == 0
                mock_island.push.assert_called_once()


class TestBotCommands:
    """Tests for Discord bot command handlers.

    Note: The @bot.command decorator is mocked, which replaces async functions
    with MagicMock objects. The underlying business logic functions are thoroughly
    tested above. Command handlers are thin wrappers that call ctx.send() with
    the result of these functions.
    """

    def test_command_functions_defined(self, fresh_bot_module):
        """Verify all command functions are defined in the module."""
        # These are replaced by MagicMock due to the mocked decorator,
        # but we verify they exist in the module namespace
        assert hasattr(fresh_bot_module, 'turnip')
        assert hasattr(fresh_bot_module, 'register_user')
        assert hasattr(fresh_bot_module, 'unregister_user')
        assert hasattr(fresh_bot_module, 'set_turnip_price')
        assert hasattr(fresh_bot_module, 'get_my_price')
        assert hasattr(fresh_bot_module, 'get_target_price')
        assert hasattr(fresh_bot_module, 'get_best_price')
        assert hasattr(fresh_bot_module, 'what_is_my_island')
        assert hasattr(fresh_bot_module, 'list_islands')
        assert hasattr(fresh_bot_module, 'get_residents')
        assert hasattr(fresh_bot_module, 'predict_turnips')
        assert hasattr(fresh_bot_module, 'reset_week')
        assert hasattr(fresh_bot_module, 'help_turnip')

    def test_slot_lookup_dictionary(self, fresh_bot_module):
        """Verify slot_lookup contains all time slots."""
        assert len(fresh_bot_module.slot_lookup) == 12
        assert fresh_bot_module.slot_lookup["Mon AM"] == 0
        assert fresh_bot_module.slot_lookup["Mon PM"] == 1
        assert fresh_bot_module.slot_lookup["Sat PM"] == 11

    def test_week_dictionary(self, fresh_bot_module):
        """Verify week dictionary maps to correct days."""
        assert len(fresh_bot_module.week) == 6
        assert fresh_bot_module.week[0] == "Mon "
        assert fresh_bot_module.week[5] == "Sat "


class TestRun:
    """Tests for run function."""

    def test_run_starts_bot(self, fresh_bot_module):
        """Test run function starts the bot."""
        fresh_bot_module.run()
        fresh_bot_module.bot.run.assert_called_once()
