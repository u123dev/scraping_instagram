import os
import random
import re
import time


def is_docker():
    return os.getenv("DOCKER") is not None


def timeout(interval_from: float = 5, interval_to: float = 7):
    time.sleep(random.uniform(interval_from, interval_to))


def text2int(text: str) -> int:
    # Удаляем все нецифровые символы с помощью регулярного выражения
    try:
        cleaned_text = re.sub(r'\D', '', text)
        return int(cleaned_text)
    except ValueError:
        return 0


def clean_text(text: str) -> str:
    # Удаляем непечатные unicode символы
    return re.sub(
        r"[\u200B\u200C\u200D\u200E\u200F\u202A-\u202E\u2060\u2061\u2062\u2063\uFEFF]",
        "",
        text
    )
