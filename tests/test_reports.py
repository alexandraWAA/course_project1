"""Тесты для отчетов."""
import pandas as pd
import pytest
from datetime import datetime

from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday
)


class TestReports:
    """Тесты отчетов."""

    @pytest.fixture
    def sample_transactions(self) -> pd.DataFrame:
        """Фикстура с тестовыми транзакциями."""
        return pd.DataFrame({
            'Дата операции': pd.date_range('2024-01-01', periods=10, freq='D'),
            'Категория': ['Супермаркеты'] * 5 + ['Рестораны'] * 5,
            'Сумма платежа': [-100, -200, -150, -300, -250, -500, -400, -600, -350, -450]
        })

    def test_spending_by_category(self, sample_transactions: pd.DataFrame) -> None:
        """Тест трат по категории."""
        result = spending_by_category(sample_transactions, 'Супермаркеты', '2024-01-10')

        assert not result.empty
        assert 'month' in result.columns
        assert 'total_spent' in result.columns

    def test_spending_by_weekday(self, sample_transactions: pd.DataFrame) -> None:
        """Тест трат по дням недели."""
        result = spending_by_weekday(sample_transactions, '2024-01-10')

        assert not result.empty
        assert 'weekday' in result.columns
        assert 'average_spent' in result.columns

    def test_spending_by_workday(self, sample_transactions: pd.DataFrame) -> None:
        """Тест трат в рабочие/выходные дни."""
        result = spending_by_workday(sample_transactions, '2024-01-10')

        assert not result.empty
        assert 'day_type' in result.columns
        assert 'average_spent' in result.columns
        assert len(result) == 2  # Рабочие дни и выходные