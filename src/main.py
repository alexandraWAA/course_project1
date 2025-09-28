"""Основной модуль приложения."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from src.views import main_page_data, events_page_data
from src.services import (
    profitable_cashback_categories,
    investment_bank,
    simple_search,
    search_phone_numbers,
    search_person_transfers
)
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.utils import load_transactions_data

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def demonstrate_views() -> None:
    """Демонстрация работы веб-страниц."""
    print("=" * 50)
    print("ДЕМОНСТРАЦИЯ ВЕБ-СТРАНИЦ")
    print("=" * 50)

    # Главная страница
    print("\n1. Главная страница:")
    main_data = main_page_data("2024-01-15 14:30:00")
    print(f"Приветствие: {main_data['greeting']}")
    print(f"Количество карт: {len(main_data['cards'])}")
    print(f"Топ транзакций: {len(main_data['top_transactions'])}")
    print(f"Курсы валют: {len(main_data['currency_rates'])}")
    print(f"Цены акций: {len(main_data['stock_prices'])}")

    # Страница событий
    print("\n2. Страница событий:")
    events_data = events_page_data("2024-01-15", "M")
    print(f"Общие расходы: {events_data['expenses']['total_amount']}")
    print(f"Основные категории расходов: {len(events_data['expenses']['main'])}")
    print(f"Общие поступления: {events_data['income']['total_amount']}")


def demonstrate_services() -> None:
    """Демонстрация работы сервисов."""
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ СЕРВИСОВ")
    print("=" * 50)

    # Загружаем данные
    df = load_transactions_data()
    transactions = df.to_dict('records')

    # Выгодные категории кешбэка
    print("\n1. Выгодные категории кешбэка:")
    cashback_categories = profitable_cashback_categories(transactions, 2024, 1)
    for category, amount in list(cashback_categories.items())[:5]:
        print(f"  {category}: {amount:.2f} руб.")

    # Инвесткопилка
    print("\n2. Инвесткопилка:")
    investment = investment_bank("2024-01", transactions, 50)
    print(f"  Сумма для инвесткопилки: {investment:.2f} руб.")

    # Простой поиск
    print("\n3. Простой поиск:")
    search_results = simple_search("магазин", transactions)
    print(f"  Найдено транзакций: {len(search_results)}")

    # Поиск телефонных номеров
    print("\n4. Поиск телефонных номеров:")
    phone_results = search_phone_numbers(transactions)
    print(f"  Найдено транзакций с телефонами: {len(phone_results)}")

    # Поиск переводов физлицам
    print("\n5. Поиск переводов физлицам:")
    person_transfers = search_person_transfers(transactions)
    print(f"  Найдено переводов физлицам: {len(person_transfers)}")


def demonstrate_reports() -> None:
    """Демонстрация работы отчетов."""
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ОТЧЕТОВ")
    print("=" * 50)

    # Загружаем данные
    df = load_transactions_data()

    # Траты по категории
    print("\n1. Траты по категории:")
    category_spending = spending_by_category(df, "Супермаркеты", "2024-01-15")
    if not category_spending.empty:
        print(category_spending.to_string(index=False))

    # Траты по дням недели
    print("\n2. Траты по дням недели:")
    weekday_spending = spending_by_weekday(df, "2024-01-15")
    if not weekday_spending.empty:
        print(weekday_spending.to_string(index=False))

    # Траты в рабочие/выходные дни
    print("\n3. Траты в рабочие/выходные дни:")
    workday_spending = spending_by_workday(df, "2024-01-15")
    if not workday_spending.empty:
        print(workday_spending.to_string(index=False))


def main() -> None:
    """Основная функция приложения."""
    try:
        logger.info("Запуск приложения анализа транзакций")

        print("ПРИЛОЖЕНИЕ ДЛЯ АНАЛИЗА БАНКОВСКИХ ТРАНЗАКЦИЙ")
        print("=" * 50)

        # Демонстрация всех функциональностей
        demonstrate_views()
        demonstrate_services()
        demonstrate_reports()

        print("\n" + "=" * 50)
        print("ВСЕ ФУНКЦИОНАЛЬНОСТИ УСПЕШНО ПРОДЕМОНСТРИРОВАНЫ")
        print("Подробные логи сохранены в файле app.log")
        print("Отчеты сохранены в JSON файлах")

        logger.info("Приложение завершило работу успешно")

    except Exception as e:
        logger.error(f"Критическая ошибка в основном модуле: {e}")
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()