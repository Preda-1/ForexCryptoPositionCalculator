"""Core calculation utilities for the Forex & Crypto Position Calculator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

InstrumentType = Literal["Forex", "Crypto"]
PositionType = Literal["Long", "Short"]

STANDARD_LOT_SIZE = 100_000
SUPPORTED_ACCOUNT_CURRENCIES = {"USD"}

__all__ = [
    "InstrumentType",
    "PositionType",
    "TradeMetrics",
    "TradeParameters",
    "calculate_distance",
    "calculate_pnl",
    "calculate_position_size",
    "calculate_risk_amount",
    "calculate_risk_reward_ratio",
    "calculate_trade_metrics",
    "get_pip_size",
    "get_pip_value_per_standard_lot",
    "normalize_currency_pair",
    "validate_trade_parameters",
]


@dataclass(frozen=True)
class TradeParameters:
    """Container for the user supplied trade inputs."""

    capital: float
    risk_percentage: float
    entry_price: float
    stop_loss_price: float
    position_type: PositionType
    instrument_type: InstrumentType
    take_profit_price: Optional[float] = None
    currency_pair: Optional[str] = None
    account_currency: str = "USD"


@dataclass(frozen=True)
class TradeMetrics:
    """Set of calculated outputs derived from :class:`TradeParameters`."""

    risk_amount: float
    stop_loss_distance: float
    position_size: float
    risk_reward_ratio: Optional[float]
    potential_pnl: Optional[float]
    currency_pair: Optional[str] = None


def calculate_trade_metrics(params: TradeParameters) -> TradeMetrics:
    """Compute the complete set of trade metrics for the provided inputs.

    Args:
        params: The trade configuration supplied by the user.

    Returns:
        A :class:`TradeMetrics` instance containing risk, size and P&L data.
    """

    normalized_pair, take_profit_price = validate_trade_parameters(params)

    risk_amount = calculate_risk_amount(params.capital, params.risk_percentage)
    stop_loss_distance = calculate_distance(
        params.entry_price,
        params.stop_loss_price,
        params.position_type,
    )
    position_size = calculate_position_size(
        risk_amount=risk_amount,
        stop_loss_distance=stop_loss_distance,
        instrument_type=params.instrument_type,
        entry_price=params.entry_price,
        currency_pair=normalized_pair,
        account_currency=params.account_currency,
    )

    risk_reward_ratio: Optional[float] = None
    potential_pnl: Optional[float] = None
    if take_profit_price is not None:
        risk_reward_ratio = calculate_risk_reward_ratio(
            params.entry_price,
            params.stop_loss_price,
            take_profit_price,
            params.position_type,
        )
        potential_pnl = calculate_pnl(
            entry_price=params.entry_price,
            take_profit_price=take_profit_price,
            position_size=position_size,
            position_type=params.position_type,
            instrument_type=params.instrument_type,
            currency_pair=normalized_pair,
            account_currency=params.account_currency,
        )

    return TradeMetrics(
        risk_amount=risk_amount,
        stop_loss_distance=stop_loss_distance,
        position_size=position_size,
        risk_reward_ratio=risk_reward_ratio,
        potential_pnl=potential_pnl,
        currency_pair=normalized_pair,
    )


def calculate_risk_amount(capital: float, risk_percentage: float) -> float:
    """Return the amount of capital placed at risk for a trade."""

    if capital <= 0:
        raise ValueError("Capital must be greater than zero.")
    if not (0 < risk_percentage < 100):
        raise ValueError("Risk percentage must be greater than 0 and less than 100.")

    return (risk_percentage / 100) * capital


def calculate_distance(
    entry_price: float,
    stop_loss_price: float,
    position_type: PositionType,
) -> float:
    """Return the stop-loss distance for the specified position type."""

    if position_type not in ("Long", "Short"):
        raise ValueError("Position type must be 'Long' or 'Short'.")

    if position_type == "Long":
        distance = entry_price - stop_loss_price
    else:
        distance = stop_loss_price - entry_price

    if distance <= 0:
        raise ValueError("Stop-loss price must create a positive distance.")

    return distance


def calculate_position_size(
    risk_amount: float,
    stop_loss_distance: float,
    instrument_type: InstrumentType,
    entry_price: float,
    currency_pair: Optional[str],
    account_currency: str = "USD",
) -> float:
    """Return the position size expressed in lots (Forex) or units (Crypto)."""

    if risk_amount <= 0:
        raise ValueError("Risk amount must be greater than zero.")
    if stop_loss_distance <= 0:
        raise ValueError("Stop-loss distance must be greater than zero.")

    if instrument_type == "Forex":
        if not currency_pair:
            raise ValueError("Currency pair is required for Forex trades.")

        pip_size = get_pip_size(currency_pair)
        pip_value = get_pip_value_per_standard_lot(
            currency_pair=currency_pair,
            entry_price=entry_price,
            account_currency=account_currency,
        )
        stop_loss_pips = stop_loss_distance / pip_size
        if stop_loss_pips <= 0:
            raise ValueError("Stop-loss distance must translate to a positive pip value.")
        return risk_amount / (stop_loss_pips * pip_value)

    if instrument_type == "Crypto":
        return risk_amount / stop_loss_distance

    raise ValueError("Instrument type must be either 'Forex' or 'Crypto'.")


def calculate_risk_reward_ratio(
    entry_price: float,
    stop_loss_price: float,
    take_profit_price: float,
    position_type: PositionType,
) -> float:
    """Return the risk-to-reward ratio for the proposed trade."""

    risk = calculate_distance(entry_price, stop_loss_price, position_type)
    if position_type == "Long":
        reward = take_profit_price - entry_price
    else:
        reward = entry_price - take_profit_price

    if reward <= 0:
        raise ValueError("Take-profit price must create a positive reward.")

    return reward / risk


def calculate_pnl(
    entry_price: float,
    take_profit_price: float,
    position_size: float,
    position_type: PositionType,
    instrument_type: InstrumentType,
    currency_pair: Optional[str],
    account_currency: str = "USD",
) -> float:
    """Return the potential profit (or loss) at the specified take-profit."""

    if instrument_type == "Forex":
        if not currency_pair:
            raise ValueError("Currency pair is required for Forex P&L calculations.")
        pip_size = get_pip_size(currency_pair)
        pip_value = get_pip_value_per_standard_lot(
            currency_pair=currency_pair,
            entry_price=entry_price,
            account_currency=account_currency,
        )
        pip_difference = abs(take_profit_price - entry_price) / pip_size
        return pip_difference * pip_value * position_size

    if instrument_type == "Crypto":
        if position_type == "Long":
            return (take_profit_price - entry_price) * position_size
        return (entry_price - take_profit_price) * position_size

    raise ValueError("Instrument type must be either 'Forex' or 'Crypto'.")


def get_pip_size(currency_pair: str) -> float:
    """Return the pip size for the supplied 3-3 currency pair."""

    base, quote = currency_pair.split("/")
    if len(base) != 3 or len(quote) != 3:
        raise ValueError("Currency pairs must be supplied in a 3-letter format (e.g., EUR/USD).")

    if quote == "JPY":
        return 0.01

    return 0.0001


def get_pip_value_per_standard_lot(
    currency_pair: str,
    entry_price: float,
    account_currency: str = "USD",
) -> float:
    """Return the pip value per standard lot for the given currency pair."""

    if account_currency not in SUPPORTED_ACCOUNT_CURRENCIES:
        raise ValueError(f"{account_currency} accounts are not supported in this version.")

    base_currency, quote_currency = currency_pair.split("/")
    pip_size = get_pip_size(currency_pair)

    if quote_currency == account_currency:
        return pip_size * STANDARD_LOT_SIZE
    if base_currency == account_currency:
        return (pip_size / entry_price) * STANDARD_LOT_SIZE

    raise ValueError(
        "Only currency pairs that include the account currency (USD) are supported."
    )


def normalize_currency_pair(currency_pair: str) -> str:
    """Return a normalised currency pair in the form XXX/YYY."""

    if not currency_pair:
        raise ValueError("Currency pair is required for Forex calculations.")

    sanitized = currency_pair.strip().upper().replace(" ", "")
    sanitized = sanitized.replace("-", "").replace("_", "")

    if "/" in sanitized:
        parts = sanitized.split("/")
    elif len(sanitized) == 6:
        parts = [sanitized[:3], sanitized[3:]]
    else:
        raise ValueError(
            "Currency pairs must contain two ISO currency codes (e.g., EUR/USD)."
        )

    if len(parts) != 2:
        raise ValueError("Currency pairs must contain exactly two components.")

    base, quote = parts
    if len(base) != 3 or len(quote) != 3 or not base.isalpha() or not quote.isalpha():
        raise ValueError(
            "Currency pairs must be comprised of alphabetic ISO currency codes."
        )

    return f"{base}/{quote}"


def validate_trade_parameters(
    params: TradeParameters,
) -> Tuple[Optional[str], Optional[float]]:
    """Validate inputs and return normalised data for downstream calculations."""

    if params.instrument_type not in ("Forex", "Crypto"):
        raise ValueError("Instrument type must be either 'Forex' or 'Crypto'.")
    if params.position_type not in ("Long", "Short"):
        raise ValueError("Position type must be 'Long' or 'Short'.")

    if params.capital <= 0:
        raise ValueError("Capital must be greater than zero.")
    if not (0 < params.risk_percentage < 100):
        raise ValueError("Risk percentage must be greater than 0 and less than 100.")
    if params.entry_price <= 0:
        raise ValueError("Entry price must be greater than zero.")
    if params.stop_loss_price <= 0:
        raise ValueError("Stop-loss price must be greater than zero.")
    if params.account_currency not in SUPPORTED_ACCOUNT_CURRENCIES:
        raise ValueError(
            f"Only {', '.join(sorted(SUPPORTED_ACCOUNT_CURRENCIES))} accounts are supported."
        )

    take_profit_price = params.take_profit_price
    if take_profit_price is not None and take_profit_price <= 0:
        raise ValueError("Take-profit price must be greater than zero when supplied.")
    if take_profit_price is not None and take_profit_price == params.entry_price:
        raise ValueError("Take-profit price cannot be equal to the entry price.")

    if params.position_type == "Long":
        if params.stop_loss_price >= params.entry_price:
            raise ValueError("For long positions, the stop-loss must be below the entry price.")
        if take_profit_price is not None and take_profit_price <= params.entry_price:
            raise ValueError("For long positions, the take-profit must be above the entry price.")
    else:
        if params.stop_loss_price <= params.entry_price:
            raise ValueError("For short positions, the stop-loss must be above the entry price.")
        if take_profit_price is not None and take_profit_price >= params.entry_price:
            raise ValueError("For short positions, the take-profit must be below the entry price.")

    normalized_pair: Optional[str] = None
    if params.instrument_type == "Forex":
        if not params.currency_pair:
            raise ValueError("Please provide a currency pair for Forex trades.")
        normalized_pair = normalize_currency_pair(params.currency_pair)

    return normalized_pair, take_profit_price
