"""Конфигурация приложения — переменные окружения."""
import os

DATABASE_URL = os.getenv("DATABASE_URL")
TG_TOKEN = os.getenv("TG_TOKEN")
SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "http://server:8000")