"""Foreign-exchange rates for expense lines.

Every amount a report is judged on lives in `BASE_CURRENCY`: the report total,
the band that picks the approval chain, and the per-expense and daily category
caps all read `amount_base`. A line captured in another currency therefore needs
a real rate, and until now it was written as 1 — a 204.76 MXN taxi was routed and
capped as if it were 204.76 USD.

The rate is resolved server-side and **frozen onto the line** when it is saved.
That is deliberate: an approved report must not silently change value because the
market moved, and an approver has to be able to see the number that was applied.

Source is the currency-api dataset served from a public CDN: no key, no quota,
daily history back several years, and it covers every currency the module
offers (USD, MXN, DOP, EUR). It is reachable through one setting so a deployment
behind a proxy, or a future paid feed, is a config change and not a code change.
"""

import logging
import os
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

import httpx

from models.expenses import BASE_CURRENCY

logger = logging.getLogger(__name__)

FX_PROVIDER_URL = os.getenv(
    "FX_PROVIDER_URL",
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{version}/v1/currencies/{base}.json",
)
FX_TIMEOUT_SECONDS = float(os.getenv("FX_TIMEOUT_SECONDS", "8"))

# A weekend or a holiday has no quote, so the nearest earlier publication is used.
MAX_LOOKBACK_DAYS = 5

# Rates are immutable once published, so a dated answer can be kept for the life
# of the process. Only the moving "latest" entry is refreshed, by keying it on
# today's date.
_cache: dict[tuple[str, str], Decimal] = {}


def _fetch(version: str, currency: str) -> dict | None:
    url = FX_PROVIDER_URL.format(version=version, base=currency.lower())
    try:
        response = httpx.get(url, timeout=FX_TIMEOUT_SECONDS, follow_redirects=True)
    except httpx.HTTPError as exc:
        logger.warning("[EXPENSES] FX request failed for %s @ %s: %s", currency, version, exc)
        return None

    if response.status_code == 404:
        # No publication for that day; the caller walks back to an earlier one.
        return None
    if response.status_code != 200:
        logger.warning(
            "[EXPENSES] FX provider answered %s for %s @ %s", response.status_code, currency, version
        )
        return None

    try:
        return response.json()
    except ValueError:
        logger.warning("[EXPENSES] FX provider returned non-JSON for %s @ %s", currency, version)
        return None


def _read_rate(payload: dict, currency: str) -> Decimal | None:
    quotes = payload.get(currency.lower())
    if not isinstance(quotes, dict):
        return None
    raw = quotes.get(BASE_CURRENCY.lower())
    if raw is None:
        return None
    try:
        rate = Decimal(str(raw))
    except (InvalidOperation, TypeError):
        return None
    return rate if rate > 0 else None


def rate_to_base(currency: str, on_date: date | None = None) -> Decimal | None:
    """Units of `BASE_CURRENCY` per one unit of `currency`, or None if unknown.

    None means "do not guess": the caller keeps the line unconverted and the
    policy engine raises a flag, which is far safer than inventing a rate and
    quietly routing the report to the wrong approval band.
    """
    currency = (currency or "").strip().upper()
    if not currency or currency == BASE_CURRENCY:
        return Decimal(1)

    # Undated lookups still key the cache on today, so "latest" refreshes daily.
    target = on_date or date.today()
    cache_key = (currency, target.isoformat())
    if cache_key in _cache:
        return _cache[cache_key]

    for offset in range(MAX_LOOKBACK_DAYS + 1):
        day = target - timedelta(days=offset)
        # A future expense date has no publication yet: ask for the newest one.
        version = "latest" if day >= date.today() else day.isoformat()
        payload = _fetch(version, currency)
        if payload is None:
            continue
        rate = _read_rate(payload, currency)
        if rate is not None:
            _cache[cache_key] = rate
            return rate

    logger.warning("[EXPENSES] No FX rate found for %s around %s", currency, target)
    return None


def clear_cache() -> None:
    """Drop memoised rates. Used by tests; harmless in production."""
    _cache.clear()
