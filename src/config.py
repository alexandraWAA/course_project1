"""Конфигурация приложения."""
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Класс конфигурации приложения."""

    # API Keys
    CURRENCY_API_KEY: Optional[str] = os.getenv('CURRENCY_API_KEY')
    STOCK_API_KEY: Optional[str] = os.getenv('STOCK_API_KEY')

    # API URLs
    CURRENCY_API_URL: str = os.getenv('CURRENCY_API_URL', 'https://api.exchangerate-api.com/v4/latest/RUB')
    STOCK_API_URL: str = os.getenv('STOCK_API_URL', 'https://www.alphavantage.co/query')

    # File paths
    DATA_FILE_PATH: str = 'data/operations.xlsx'
    USER_SETTINGS_PATH: str = 'user_settings.json'

    # Default values
    DEFAULT_CURRENCIES: List[str] = ['USD', 'EUR']
    DEFAULT_STOCKS: List[str] = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']