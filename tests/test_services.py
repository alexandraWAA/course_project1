"""Тесты для сервисов."""
import pytest
from unittest.mock import patch

from src.services import (
    simple_search,
    search_phone_numbers,
    search_person_transfers
)


class TestServices:
    """Тесты сервисов."""

    def test_simple_search(self) -> None:
        """Тест простого поиска."""
        transactions = [
            {'Описание': 'Покупка в магазине', 'Категория': 'Супермаркет'},
            {'Описание': 'Оплата услуг', 'Категория': 'Услуги'},
            {'Описание': 'Магазин электроники', 'Категория': 'Техника'},
        ]

        result = simple_search('магазин', transactions)

        assert len(result) == 2
        assert all('магазин' in str(t['Описание']).lower() or 'магазин' in str(t['Категория']).lower()
                   for t in result)

    def test_search_phone_numbers(self) -> None:
        """Тест поиска телефонных номеров."""
        transactions = [
            {'Описание': 'Пополнение +7 921 123-45-67'},
            {'Описание': 'Перевод 8(995)555-55-55'},
            {'Описание': 'Оплата без телефона'},
        ]

        result = search_phone_numbers(transactions)

        assert len(result) == 2
        assert any('+7 921 123-45-67' in t['Описание'] for t in result)
        assert any('8(995)555-55-55' in t['Описание'] for t in result)

    def test_search_person_transfers(self) -> None:
        """Тест поиска переводов физлицам."""
        transactions = [
            {'Описание': 'Перевод Ивану И.', 'Категория': 'Переводы'},
            {'Описание': 'Перевод Петр П.', 'Категория': 'Переводы'},
            {'Описание': 'Магазин без перевода', 'Категория': 'Супермаркет'},
        ]

        result = search_person_transfers(transactions)

        assert len(result) == 2
        assert all(t['Категория'] == 'Переводы' for t in result)
        assert any('Иван' in t['Описание'] for t in result)
        assert any('Петр' in t['Описание'] for t in result)