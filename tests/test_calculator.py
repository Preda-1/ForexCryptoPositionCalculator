"""Unit tests for the calculator module."""

import math

import pytest

from calculator import (
    TradeParameters,
    calculate_distance,
    calculate_trade_metrics,
    get_pip_value_per_standard_lot,
    normalize_currency_pair,
)


def test_calculate_trade_metrics_forex_long() -> None:
    params = TradeParameters(
        capital=10_000,
        risk_percentage=1.5,
        entry_price=1.2050,
        stop_loss_price=1.2000,
        take_profit_price=1.2200,
        position_type="Long",
        instrument_type="Forex",
        currency_pair="eurusd",
    )

    metrics = calculate_trade_metrics(params)

    assert math.isclose(metrics.risk_amount, 150.0, rel_tol=1e-9)
    assert metrics.currency_pair == "EUR/USD"
    assert metrics.risk_reward_ratio is not None
    assert metrics.potential_pnl is not None
    assert metrics.position_size > 0
    assert metrics.stop_loss_distance > 0


def test_calculate_trade_metrics_crypto_short() -> None:
    params = TradeParameters(
        capital=5_000,
        risk_percentage=2,
        entry_price=28_000,
        stop_loss_price=29_000,
        take_profit_price=25_000,
        position_type="Short",
        instrument_type="Crypto",
    )

    metrics = calculate_trade_metrics(params)

    assert math.isclose(metrics.risk_amount, 100.0, rel_tol=1e-9)
    assert math.isclose(metrics.position_size, 0.1, rel_tol=1e-9)
    assert metrics.currency_pair is None
    assert metrics.risk_reward_ratio == pytest.approx(3.0, rel=1e-9)
    assert metrics.potential_pnl == pytest.approx(300.0, rel=1e-9)


def test_distance_validation() -> None:
    with pytest.raises(ValueError):
        calculate_distance(entry_price=1.2, stop_loss_price=1.3, position_type="Long")


def test_pip_value_for_usdjpy() -> None:
    pip_value = get_pip_value_per_standard_lot("USD/JPY", entry_price=110.0)
    assert pip_value == pytest.approx(9.0909, rel=1e-4)


def test_normalize_currency_pair_variants() -> None:
    assert normalize_currency_pair("gbp_jpy") == "GBP/JPY"
    assert normalize_currency_pair("audcad") == "AUD/CAD"

    with pytest.raises(ValueError):
        normalize_currency_pair("invalid")
