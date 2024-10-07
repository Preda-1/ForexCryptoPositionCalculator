# calculator.py

def calculate_risk_amount(capital, risk_percentage):
    """
    Calculate the amount of capital risked per trade.
    """
    return (risk_percentage / 100) * capital

def calculate_distance(entry_price, stop_loss_price):
    """
    Calculate the distance between entry price and stop-loss.
    """
    return abs(entry_price - stop_loss_price)

def calculate_position_size(risk_amount, distance, instrument_type, entry_price, currency_pair, account_currency="USD"):
    """
    Calculate the position size based on the instrument type.
    """
    if distance == 0:
        raise ValueError("Stop-loss distance cannot be zero.")

    if instrument_type == "Forex":
        # For Forex, calculate position size in lots
        pip_size = get_pip_size(currency_pair)
        stop_loss_pips = distance / pip_size

        pip_value_per_lot = get_pip_value_per_standard_lot(currency_pair, entry_price, account_currency)

        if pip_value_per_lot == 0:
            raise ValueError("Calculation for this currency pair is not supported in this version.")

        position_size_in_lots = risk_amount / (stop_loss_pips * pip_value_per_lot)
        return position_size_in_lots
    else:
        # For Crypto, position size is in units
        return risk_amount / distance

def calculate_risk_reward_ratio(entry_price, stop_loss_price, take_profit_price, position_type):
    """
    Calculate the risk-reward ratio.
    """
    risk = abs(entry_price - stop_loss_price)
    reward = abs(take_profit_price - entry_price)
    if position_type == "Short":
        reward = abs(entry_price - take_profit_price)
    if risk == 0:
        raise ValueError("Risk cannot be zero.")
    return reward / risk

def calculate_pnl(entry_price, take_profit_price, position_size, position_type, instrument_type, currency_pair, account_currency="USD"):
    """
    Calculate the potential Profit and Loss (P&L).
    """
    if instrument_type == "Forex":
        pip_size = get_pip_size(currency_pair)
        pip_value_per_lot = get_pip_value_per_standard_lot(currency_pair, entry_price, account_currency)
        pip_difference = abs(take_profit_price - entry_price) / pip_size

        if pip_value_per_lot == 0:
            raise ValueError("Calculation for this currency pair is not supported in this version.")

        pnl = pip_difference * pip_value_per_lot * position_size
    else:
        if position_type == "Long":
            pnl = (take_profit_price - entry_price) * position_size
        else:
            pnl = (entry_price - take_profit_price) * position_size
    return pnl

def get_pip_size(currency_pair):
    """
    Determine the pip size based on the currency pair.
    """
    if "JPY" in currency_pair:
        return 0.01
    else:
        return 0.0001

def get_pip_value_per_standard_lot(currency_pair, entry_price, account_currency="USD"):
    """
    Calculate the pip value per standard lot (100,000 units).
    """
    # For USD account
    if currency_pair.endswith("USD"):
        # USD is the quote currency
        return 10  # $10 per pip per standard lot
    elif currency_pair.startswith("USD"):
        # USD is the base currency
        return 10 / entry_price  # Adjusted pip value per standard lot
    else:
        # Cross pairs not supported in this version
        return 0  # Indicate unsupported currency pair
