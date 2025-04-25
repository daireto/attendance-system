import random
import unicodedata
from datetime import datetime, timedelta, timezone


def random_datetime(
    min_year: int = 1900,
    max_year: int = datetime.now().year,
    tz: timezone | None = None,
) -> datetime:
    """Generates a random datetime.

    Parameters
    ----------
    min_year : int, optional
        Minimum year, by default 1900.
    max_year : int, optional
        Maximum year, by default ``datetime.now().year``.
    tz : timezone, optional
        Timezone, by default None.

    Returns
    -------
    datetime
        Generated datetime.
    """
    start = datetime(min_year, 1, 1, 00, 00, 00, tzinfo=tz)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()


def strip_accents(text: str) -> str:
    """Removes accents from a string.

    Parameters
    ----------
    text : str
        String to strip accents from.

    Returns
    -------
    str
        String without accents.
    """
    return ''.join(
        [
            c
            for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        ]
    )
