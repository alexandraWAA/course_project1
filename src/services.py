"""Сервисы для анализа транзакций."""
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from collections import Counter

import pandas as pd

from src.utils import load_transactions_data

logger = logging.getLogger(__name__)


def profitable_cashback_categories(
        data: List[Dict[str, Any]],
        year: int,
        month: int
) -> Dict[str, float]:
    """
    Анализирует выгодность категорий повышенного кешбэка.

    Args:
        data: Список транзакций
        year: Год для анализа
        month: Месяц для анализа

    Returns:
        Словарь с категориями и суммами кешбэка
    """
    try:
        logger.info(f"Анализ выгодных категорий кешбэка за {year}-{month}")

        # Преобразуем в DataFrame для удобства
        df = pd.DataFrame(data)

        # Фильтруем по дате
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        df['Дата операции'] = pd.to_datetime(df['Дата операции'])
        mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] < end_date)
        monthly_data = df[mask].copy()

        # Рассчитываем кешбэк по категориям (1% от суммы расходов)
        expenses = monthly_data[monthly_data['Сумма платежа'] < 0].copy()
        expenses['cashback'] = expenses['Сумма платежа'].abs() * 0.01

        category_cashback = expenses.groupby('Категория')['cashback'].sum().round(2)

        result = category_cashback.to_dict()
        logger.info(f"Проанализировано {len(result)} категорий")

        return result

    except Exception as e:
        logger.error(f"Ошибка анализа выгодных категорий: {e}")
        return {}


def investment_bank(
        month: str,
        transactions: List[Dict[str, Any]],
        limit: int
) -> float:
    """
    Рассчитывает сумму для инвесткопилки через округление трат.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Предел округления (10, 50, 100)

    Returns:
        Сумма для инвесткопилки
    """
    try:
        logger.info(f"Расчет инвесткопилки за {month} с лимитом {limit}")

        df = pd.DataFrame(transactions)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'])

        # Фильтруем по месяцу
        year, month_num = map(int, month.split('-'))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month_num + 1, 1)

        mask = (df['Дата операции'] >= start_date) & (df['Дата операции'] < end_date)
        monthly_data = df[mask].copy()

        # Берем только расходы
        expenses = monthly_data[monthly_data['Сумма платежа'] < 0].copy()
        expenses['amount_abs'] = expenses['Сумма платежа'].abs()

        # Округляем суммы до ближайшего limit
        expenses['rounded'] = (expenses['amount_abs'] / limit).apply(lambda x: limit * (x // 1 + 1))
        expenses['investment'] = expenses['rounded'] - expenses['amount_abs']

        total_investment = expenses['investment'].sum()

        logger.info(f"Сумма для инвесткопилки: {total_investment:.2f}")
        return round(total_investment, 2)

    except Exception as e:
        logger.error(f"Ошибка расчета инвесткопилки: {e}")
        return 0.0


def simple_search(
        search_query: str,
        transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Простой поиск транзакций по описанию или категории.

    Args:
        search_query: Строка для поиска
        transactions: Список транзакций

    Returns:
        Список найденных транзакций
    """
    try:
        logger.info(f"Поиск транзакций по запросу: '{search_query}'")

        if not search_query.strip():
            return transactions

        query_lower = search_query.lower()
        results = []

        for transaction in transactions:
            description = str(transaction.get('Описание', '')).lower()
            category = str(transaction.get('Категория', '')).lower()

            if query_lower in description or query_lower in category:
                results.append(transaction)

        logger.info(f"Найдено {len(results)} транзакций")
        return results

    except Exception as e:
        logger.error(f"Ошибка поиска транзакций: {e}")
        return []


def search_phone_numbers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Поиск транзакций с телефонными номерами в описании.

    Args:
        transactions: Список транзакций

    Returns:
        Список транзакций с телефонными номерами
    """
    try:
        logger.info("Поиск транзакций с телефонными номерами")

        # Регулярное выражение для российских мобильных номеров
        phone_pattern = r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'

        results = []
        for transaction in transactions:
            description = str(transaction.get('Описание', ''))

            if re.search(phone_pattern, description):
                results.append(transaction)

        logger.info(f"Найдено {len(results)} транзакций с телефонными номерами")
        return results

    except Exception as e:
        logger.error(f"Ошибка поиска телефонных номеров: {e}")
        return []


def search_person_transfers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Поиск переводов физическим лицам.

    Args:
        transactions: Список транзакций

    Returns:
        Список переводов физлицам
    """
    try:
        logger.info("Поиск переводов физическим лицам")

        # Паттерн для имени и первой буквы фамилии с точкой
        name_pattern = r'[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.'

        results = []
        for transaction in transactions:
            category = str(transaction.get('Категория', ''))
            description = str(transaction.get('Описание', ''))

            # Проверяем категорию "Переводы" и паттерн имени в описании
            if category == 'Переводы' and re.search(name_pattern, description):
                results.append(transaction)

        logger.info(f"Найдено {len(results)} переводов физлицам")
        return results

    except Exception as e:
        logger.error(f"Ошибка поиска переводов физлицам: {e}")
        return []