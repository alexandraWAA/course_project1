"""Утилиты для работы с данными."""
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import pandas as pd
import requests

from src.config import Config

logger = logging.getLogger(__name__)


def load_transactions_data(file_path: str = Config.DATA_FILE_PATH) -> pd.DataFrame:
    """
    Загружает данные транзакций из Excel файла.

    Args:
        file_path: Путь к Excel файлу

    Returns:
        DataFrame с транзакциями
    """
    try:
        logger.info(f"Загрузка данных из файла: {file_path}")
        df = pd.read_excel(file_path)

        # Преобразование дат
        date_columns = ['Дата операции', 'Дата платежа']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        logger.info(f"Успешно загружено {len(df)} транзакций")
        return df

    except Exception as e:
        logger.error(f"Ошибка загрузки данных из {file_path}: {e}")
        raise


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки.

    Returns:
        Словарь с настройками пользователя
    """
    try:
        with open(Config.USER_SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Устанавливаем значения по умолчанию, если они отсутствуют
        settings.setdefault('user_currencies', Config.DEFAULT_CURRENCIES)
        settings.setdefault('user_stocks', Config.DEFAULT_STOCKS)

        return settings

    except FileNotFoundError:
        logger.warning(f"Файл настроек {Config.USER_SETTINGS_PATH} не найден, используются значения по умолчанию")
        return {
            'user_currencies': Config.DEFAULT_CURRENCIES,
            'user_stocks': Config.DEFAULT_STOCKS
        }
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        return {
            'user_currencies': Config.DEFAULT_CURRENCIES,
            'user_stocks': Config.DEFAULT_STOCKS
        }


def get_greeting_by_time(dt: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        dt: Дата и время

    Returns:
        Приветствие
    """
    hour = dt.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает курсы валют.

    Args:
        currencies: Список валют

    Returns:
        Список словарей с курсами валют
    """
    try:
        logger.info(f"Получение курсов валют: {currencies}")

        # Для демонстрации используем фиктивные данные
        # В реальном приложении здесь будет API запрос
        rates = []
        mock_rates = {'USD': 95.0, 'EUR': 102.0}

        for currency in currencies:
            rate = mock_rates.get(currency, 1.0)
            rates.append({
                'currency': currency,
                'rate': rate
            })

        logger.info(f"Получены курсы {len(rates)} валют")
        return rates

    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        return []


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает цены акций.

    Args:
        stocks: Список акций

    Returns:
        Список словарей с ценами акций
    """
    try:
        logger.info(f"Получение цен акций: {stocks}")

        # Для демонстрации используем фиктивные данные
        # В реальном приложении здесь будет API запрос
        prices = []
        mock_prices = {
            'AAPL': 185.0,
            'AMZN': 145.0,
            'GOOGL': 135.0,
            'MSFT': 370.0,
            'TSLA': 240.0
        }

        for stock in stocks:
            price = mock_prices.get(stock, 100.0)
            prices.append({
                'stock': stock,
                'price': price
            })

        logger.info(f"Получены цены {len(prices)} акций")
        return prices

    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        return []


def filter_data_by_date_range(
        df: pd.DataFrame,
        end_date: str,
        period: str = 'M'
) -> pd.DataFrame:
    """
    Фильтрует данные по временному диапазону.

    Args:
        df: DataFrame с транзакциями
        end_date: Конечная дата в формате 'YYYY-MM-DD'
        period: Период ('W', 'M', 'Y', 'ALL')

    Returns:
        Отфильтрованный DataFrame
    """
    try:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        date_column = 'Дата операции'

        if period == 'W':  # Неделя
            start_dt = end_dt - timedelta(days=7)
        elif period == 'M':  # Месяц
            start_dt = end_dt.replace(day=1)
        elif period == 'Y':  # Год
            start_dt = end_dt.replace(month=1, day=1)
        elif period == 'ALL':  # Все данные
            return df
        else:
            raise ValueError(f"Неизвестный период: {period}")

        mask = (df[date_column] >= start_dt) & (df[date_column] <= end_dt)
        filtered_df = df[mask].copy()

        logger.info(f"Отфильтровано {len(filtered_df)} транзакций за период {period}")
        return filtered_df

    except Exception as e:
        logger.error(f"Ошибка фильтрации данных: {e}")
        raise


def format_date_for_display(date_str: str) -> str:
    """
    Форматирует дату для отображения.

    Args:
        date_str: Дата в формате 'YYYY-MM-DD'

    Returns:
        Отформатированная дата
    """
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d.%m.%Y')
    except ValueError:
        return date_str


def calculate_cashback(amount: float) -> float:
    """
    Рассчитывает кешбэк (1% от суммы).

    Args:
        amount: Сумма операции

    Returns:
        Размер кешбэка
    """
    return round(amount * 0.01, 2)