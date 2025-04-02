from logging import getLogger
from random import choice

logger = getLogger(__name__)


def convert_time(seconds: float) -> str:
    if seconds >= 60:
        minutes = seconds // 60
        remaining_seconds = round(seconds % 60, 2)
        return "{} minutes and {} seconds".format(minutes, remaining_seconds)
    else:
        return "{} seconds".format(seconds)


def fread(filepath: str, encoding: str = 'utf-8') -> str:
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()


def get_random_user_agent() -> str:
    return choice([
        # Chrome User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.64 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36",
        # Firefox User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6; rv:107.0) Gecko/20100101 Firefox/107.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        # Safari User Agents
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.1 Safari/537.36",
        # Edge User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.78 Safari/537.36 Edg/110.0.1587.57",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.99 Safari/537.36 Edg/108.0.1462.46"
    ])


def dict_vals_exist(d: dict) -> bool:
    for k, v in d.items():
        if not v: 
            logger.error(f"Key '{k}' has invalid value.")
            return False
    return True