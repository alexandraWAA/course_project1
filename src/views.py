"""Модуль для генерации JSON-ответов для веб-страниц."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils import (
    load_transactions_data,
    load_user_settings,
    get_greeting_by_time,
    get_currency_rates,
    get_stock_prices,
    filter_data_by_date_range,
    format_date_for_display,
    calculate_cashback
)

logger = logging.getLogger(__name__)


def main_page_data(datetime_str: str) -> Dict[str, Any]:
    """
    Генерирует данные для главной страницы.

    Args:
        datetime_str: Дата и время в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        JSON-ответ для главной страницы
    """
    try:
        logger.info(f"Генерация данных для главной страницы: {datetime_str}")

        # Загрузка данных
        df = load_transactions_data()
        settings = load_user_settings()

        # Парсинг даты
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        date_str = dt.strftime('%Y-%m-%d')

        # Фильтрация данных за текущий месяц
        filtered_df = filter_data_by_date_range(df, date_str, 'M')

        # Приветствие
        greeting = get_greeting_by_time(dt)

        # Данные по картам
        cards_data = _get_cards_data(filtered_df)

        # Топ транзакций
        top_transactions = _get_top_transactions(filtered_df, 5)

        # Курсы валют
        currency_rates = get_currency_rates(settings['user_currencies'])

        # Цены акций
        stock_prices = get_stock_prices(settings['user_stocks'])

        result = {
            'greeting': greeting,
            'cards': cards_data,
            'top_transactions': top_transactions,
            'currency_rates': currency_rates,
            'stock_prices': stock_prices
        }

        logger.info("Данные для главной страницы успешно сгенерированы")
        return result

    except Exception as e:
        logger.error(f"Ошибка генерации данных главной страницы: {e}")
        return {
            'greeting': 'Добрый день',
            'cards': [],
            'top_transactions': [],
            'currency_rates': [],
            'stock_prices': []
        }


def events_page_data(date_str: str, period: str = 'M') -> Dict[str, Any]:
    """
    Генерирует данные для страницы событий.

    Args:
        date_str: Дата в формате 'YYYY-MM-DD'
        period: Период ('W', 'M', 'Y', 'ALL')

    Returns:
        JSON-ответ для страницы событий
    """
    try:
        logger.info(f"Генерация данных для страницы событий: {date_str}, период: {period}")

        # Загрузка данных
        df = load_transactions_data()
        settings = load_user_settings()

        # Фильтрация данных
        filtered_df = filter_data_by_date_range(df, date_str, period)

        # Расходы
        expenses_data = _get_expenses_data(filtered_df)

        # Поступления
        income_data = _get_income_data(filtered_df)

        # Курсы валют
        currency_rates = get_currency_rates(settings['user_currencies'])

        # Цены акций
        stock_prices = get_stock_prices(settings['user_stocks'])

        result = {
            'expenses': expenses_data,
            'income': income_data,
            'currency_rates': currency_rates,
            'stock_prices': stock_prices
        }

        logger.info("Данные для страницы событий успешно сгенерированы")
        return result

    except Exception as e:
        logger.error(f"Ошибка генерации данных страницы событий: {e}")
        return {
            'expenses': {'total_amount': 0, 'main': [], 'transfers_and_cash': []},
            'income': {'total_amount': 0, 'main': []},
            'currency_rates': [],
            'stock_prices': []
        }


def _get_cards_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Получает данные по картам."""
    if 'Номер карты' not in df.columns or 'Сумма платежа' not in df.columns:
        return []

    cards_data = []

    # Группировка по последним 4 цифрам карты
    for card_digits in df['Номер карты'].dropna().unique():
        card_df = df[df['Номер карты'] == card_digits]

        # Суммируем только расходы (отрицательные суммы)
        expenses = card_df[card_df['Сумма платежа'] < 0]['Сумма платежа'].sum()
        total_spent = abs(expenses)
        cashback = calculate_cashback(total_spent)

        cards_data.append({
            'last_digits': str(card_digits)[-4:],
            'total_spent': round(total_spent, 2),
            'cashback': round(cashback, 2)
        })

    return cards_data


def _get_top_transactions(df: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
    """Получает топ транзакций по сумме платежа."""
    if df.empty:
        return []

    # Берем транзакции с наибольшей абсолютной суммой
    top_df = df.nlargest(limit, 'Сумма платежа', keep='all')

    transactions = []
    for _, row in top_df.iterrows():
        transactions.append({
            'date': format_date_for_display(row['Дата операции'].strftime('%Y-%m-%d')),
            'amount': round(row['Сумма платежа'], 2),
            'category': row.get('Категория', 'Неизвестно'),
            'description': row.get('Описание', '')
        })

    return transactions


def _get_expenses_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Получает данные по расходам."""
    if df.empty:
        return {'total_amount': 0, 'main': [], 'transfers_and_cash': []}

    # Фильтруем расходы (отрицательные суммы)
    expenses_df = df[df['Сумма платежа'] < 0].copy()
    expenses_df['amount_abs'] = expenses_df['Сумма платежа'].abs()

    # Общая сумма расходов
    total_amount = round(expenses_df['amount_abs'].sum())

    # Основные категории расходов
    main_categories = _get_main_categories(expenses_df, 'Категория', 7)

    # Переводы и наличные
    transfers_cash = _get_transfers_and_cash(expenses_df)

    return {
        'total_amount': total_amount,
        'main': main_categories,
        'transfers_and_cash': transfers_cash
    }


def _get_income_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Получает данные по поступлениям."""
    if df.empty:
        return {'total_amount': 0, 'main': []}

    # Фильтруем поступления (положительные суммы)
    income_df = df[df['Сумма платежа'] > 0].copy()

    # Общая сумма поступлений
    total_amount = round(income_df['Сумма платежа'].sum())

    # Основные категории поступлений
    main_categories = _get_main_categories(income_df, 'Категория', 10)

    return {
        'total_amount': total_amount,
        'main': main_categories
    }


def _get_main_categories(df: pd.DataFrame, category_col: str, limit: int) -> List[Dict[str, Any]]:
    """Получает основные категории."""
    if df.empty or category_col not in df.columns:
        return []

    category_sums = df.groupby(category_col)['amount_abs'].sum().round().astype(int)
    category_sums = category_sums.sort_values(ascending=False)

    # Берем топ категорий
    main_categories = []
    other_amount = 0

    for i, (category, amount) in enumerate(category_sums.items()):
        if i < limit:
            main_categories.append({
                'category': category,
                'amount': int(amount)
            })
        else:
            other_amount += amount

    # Добавляем "Остальное" если есть
    if other_amount > 0:
        main_categories.append({
            'category': 'Остальное',
            'amount': int(other_amount)
        })

    return main_categories


def _get_transfers_and_cash(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Получает данные по переводам и наличным."""
    transfers_cash = []

    # Находим категории связанные с переводами и наличными
    transfer_categories = ['Переводы', 'Наличные']

    for category in transfer_categories:
        category_df = df[df['Категория'] == category]
        if not category_df.empty:
            amount = round(category_df['amount_abs'].sum())
            transfers_cash.append({
                'category': category,
                'amount': int(amount)
            })

    return sorted(transfers_cash, key=lambda x: x['amount'], reverse=True)