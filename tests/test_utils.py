"""Тесты для утилит."""
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

from src.utils import (
    get_greeting_by_time,
    format_date_for_display,
    calculate_cashback,
    filter_data_by_date_range
)
import pandas as pd


class TestUtils:
    """Тесты утилит."""

    @pytest.mark.parametrize("hour,expected", [
        (5, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (4, "Доброй ночи"),
    ])
    def test_get_greeting_by_time(self, hour: int, expected: str) -> None:
        """Тест приветствия по времени."""
        dt = datetime(2024, 1, 1, hour)
        result = get_greeting_by_time(dt)
        assert result == expected

    def test_format_date_for_display(self) -> None:
        """Тест форматирования даты."""
        result = format_date_for_display("2024-01-15")
        assert result == "15.01.2024"

    @pytest.mark.parametrize("amount,expected", [
        (100, 1.0),
        (500, 5.0),
        (123.45, 1.23),
        (0, 0.0),
    ])
    def test_calculate_cashback(self, amount: float, expected: float) -> None:
        """Тест расчета кешбэка."""
        result = calculate_cashback(amount)
        assert result == pytest.approx(expected, 0.01)

    def test_filter_data_by_date_range(self) -> None:
        """Тест фильтрации данных по дате."""
        # Создаем тестовые данные
        df = pd.DataFrame({
            'Дата операции': pd.date_range('2024-01-01', periods=10, freq='D'),
            'Сумма платежа': range(10)
        })

        result = filter_data_by_date_range(df, '2024-01-05', 'M')

        # Должны остаться данные с 1 по 5 января
        assert len(result) == 5
        assert result['Дата операции'].min() == pd.Timestamp('2024-01-01')
        assert result['Дата операции'].max() == pd.Timestamp('2024-01-05')