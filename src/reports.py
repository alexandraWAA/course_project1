"""Модуль для генерации отчетов."""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional
from functools import wraps

import pandas as pd

from src.utils import load_transactions_data

logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None):
    """
    Декоратор для записи результатов отчетов в файл.

    Args:
        filename: Имя файла для сохранения (если None, генерируется автоматически)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Генерируем имя файла если не указано
                if filename is None:
                    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                    report_filename = f"report_{func.__name__}_{current_time}.json"
                else:
                    report_filename = filename

                # Сохраняем результат в файл
                with open(report_filename, 'w', encoding='utf-8') as f:
                    if isinstance(result, pd.DataFrame):
                        json_str = result.to_json(orient='records', force_ascii=False, indent=2)
                        f.write(json_str)
                    else:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"Отчет сохранен в файл: {report_filename}")
                return result

            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")
                return func(*args, **kwargs)

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(
        transactions: pd.DataFrame,
        category: str,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует траты по категории за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Категория для анализа
        date: Дата отсчета (если None, используется текущая дата)

    Returns:
        DataFrame с тратами по месяцам
    """
    try:
        logger.info(f"Анализ трат по категории '{category}'")

        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, '%Y-%m-%d')

        start_date = end_date - timedelta(days=90)

        # Фильтруем данные
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
        mask = (transactions['Дата операции'] >= start_date) & (transactions['Дата операции'] <= end_date)
        filtered_data = transactions[mask].copy()

        # Фильтруем по категории и расходам
        category_data = filtered_data[
            (filtered_data['Категория'] == category) &
            (filtered_data['Сумма платежа'] < 0)
            ].copy()

        if category_data.empty:
            logger.warning(f"Нет данных по категории '{category}' за указанный период")
            return pd.DataFrame()

        # Группируем по месяцам
        category_data['month'] = category_data['Дата операции'].dt.to_period('M')
        monthly_spending = category_data.groupby('month')['Сумма платежа'].sum().abs().round(2)

        result_df = monthly_spending.reset_index()
        result_df.columns = ['month', 'total_spent']
        result_df['month'] = result_df['month'].astype(str)

        logger.info(f"Проанализированы траты по категории '{category}' за {len(result_df)} месяцев")
        return result_df

    except Exception as e:
        logger.error(f"Ошибка анализа трат по категории: {e}")
        return pd.DataFrame()


@report_decorator()
def spending_by_weekday(
        transactions: pd.DataFrame,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует средние траты по дням недели за последние три месяца.

    Args:
        transactions: DataFrame с транзакций
        date: Дата отсчета (если None, используется текущая дата)

    Returns:
        DataFrame со средними тратами по дням недели
    """
    try:
        logger.info("Анализ трат по дням недели")

        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, '%Y-%m-%d')

        start_date = end_date - timedelta(days=90)

        # Фильтруем данные
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
        mask = (transactions['Дата операции'] >= start_date) & (transactions['Дата операции'] <= end_date)
        filtered_data = transactions[mask].copy()

        # Фильтруем расходы
        expenses = filtered_data[filtered_data['Сумма платежа'] < 0].copy()
        expenses['amount_abs'] = expenses['Сумма платежа'].abs()
        expenses['weekday'] = expenses['Дата операции'].dt.day_name()

        # Средние траты по дням недели
        weekday_spending = expenses.groupby('weekday')['amount_abs'].mean().round(2)

        # Упорядочиваем дни недели
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_spending = weekday_spending.reindex(weekday_order, fill_value=0)

        result_df = weekday_spending.reset_index()
        result_df.columns = ['weekday', 'average_spent']

        logger.info("Проанализированы траты по дням недели")
        return result_df

    except Exception as e:
        logger.error(f"Ошибка анализа трат по дням недели: {e}")
        return pd.DataFrame()


@report_decorator()
def spending_by_workday(
        transactions: pd.DataFrame,
        date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует средние траты в рабочие и выходные дни.

    Args:
        transactions: DataFrame с транзакций
        date: Дата отсчета (если None, используется текущая дата)

    Returns:
        DataFrame со средними тратами по типам дней
    """
    try:
        logger.info("Анализ трат в рабочие/выходные дни")

        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, '%Y-%m-%d')

        start_date = end_date - timedelta(days=90)

        # Фильтруем данные
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'])
        mask = (transactions['Дата операции'] >= start_date) & (transactions['Дата операции'] <= end_date)
        filtered_data = transactions[mask].copy()

        # Фильтруем расходы
        expenses = filtered_data[filtered_data['Сумма платежа'] < 0].copy()
        expenses['amount_abs'] = expenses['Сумма платежа'].abs()

        # Определяем рабочие дни (пн-пт) и выходные (сб-вс)
        expenses['is_weekend'] = expenses['Дата операции'].dt.weekday >= 5

        # Средние траты по типам дней
        workday_spending = expenses.groupby('is_weekend')['amount_abs'].mean().round(2)

        result_df = workday_spending.reset_index()
        result_df['day_type'] = result_df['is_weekend'].map({False: 'Рабочие дни', True: 'Выходные дни'})
        result_df = result_df[['day_type', 'amount_abs']]
        result_df.columns = ['day_type', 'average_spent']

        logger.info("Проанализированы траты в рабочие/выходные дни")
        return result_df

    except Exception as e:
        logger.error(f"Ошибка анализа трат по типам дней: {e}")
        return pd.DataFrame()