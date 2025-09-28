"""Тесты для веб-страниц."""
from unittest.mock import patch, MagicMock
import pytest

from src.views import main_page_data, events_page_data


class TestViews:
    """Тесты веб-страниц."""

    @patch('src.views.load_transactions_data')
    @patch('src.views.load_user_settings')
    def test_main_page_data(self, mock_settings, mock_load_data) -> None:
        """Тест данных главной страницы."""
        # Мокируем данные
        mock_df = MagicMock()
        mock_load_data.return_value = mock_df
        mock_settings.return_value = {
            'user_currencies': ['USD', 'EUR'],
            'user_stocks': ['AAPL', 'TSLA']
        }

        result = main_page_data("2024-01-15 14:30:00")

        assert 'greeting' in result
        assert 'cards' in result
        assert 'top_transactions' in result
        assert 'currency_rates' in result
        assert 'stock_prices' in result
        assert result['greeting'] == "Добрый день"

    @patch('src.views.load_transactions_data')
    @patch('src.views.load_user_settings')
    def test_events_page_data(self, mock_settings, mock_load_data) -> None:
        """Тест данных страницы событий."""
        # Мокируем данные
        mock_df = MagicMock()
        mock_load_data.return_value = mock_df
        mock_settings.return_value = {
            'user_currencies': ['USD'],
            'user_stocks': ['AAPL']
        }

        result = events_page_data("2024-01-15", "M")

        assert 'expenses' in result
        assert 'income' in result
        assert 'currency_rates' in result
        assert 'stock_prices' in result
        assert 'total_amount' in result['expenses']
        assert 'main' in result['expenses']