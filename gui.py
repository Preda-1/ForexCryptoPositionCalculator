"""Tkinter graphical user interface for the position size calculator."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from calculator import (
    TradeMetrics,
    TradeParameters,
    calculate_trade_metrics,
    get_pip_size,
)


class PositionCalculatorApp:
    """Interactive desktop interface for the Forex & Crypto Position Calculator."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Forex & Crypto Position Size Calculator")
        self.root.resizable(False, False)

        self._init_variables()
        self._create_widgets()
        self._set_currency_state()

    def _init_variables(self) -> None:
        self.capital_var = tk.StringVar()
        self.risk_percentage_var = tk.StringVar()
        self.entry_price_var = tk.StringVar()
        self.stop_loss_price_var = tk.StringVar()
        self.take_profit_price_var = tk.StringVar()

        self.position_type = tk.StringVar(value="Long")
        self.instrument_type = tk.StringVar(value="Crypto")
        self.currency_pair_var = tk.StringVar(value="EUR/USD")

    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self.root, padding="16 16 16 16")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Total Capital (USD)").grid(row=0, column=0, sticky="W", pady=(0, 4))
        ttk.Entry(main_frame, textvariable=self.capital_var).grid(row=0, column=1, sticky="EW", pady=(0, 4))

        ttk.Label(main_frame, text="Risk per Trade (%)").grid(row=1, column=0, sticky="W", pady=4)
        ttk.Entry(main_frame, textvariable=self.risk_percentage_var).grid(row=1, column=1, sticky="EW", pady=4)

        ttk.Label(main_frame, text="Entry Price").grid(row=2, column=0, sticky="W", pady=4)
        ttk.Entry(main_frame, textvariable=self.entry_price_var).grid(row=2, column=1, sticky="EW", pady=4)

        ttk.Label(main_frame, text="Stop-Loss Price").grid(row=3, column=0, sticky="W", pady=4)
        ttk.Entry(main_frame, textvariable=self.stop_loss_price_var).grid(row=3, column=1, sticky="EW", pady=4)

        ttk.Label(main_frame, text="Take-Profit Price (optional)").grid(row=4, column=0, sticky="W", pady=4)
        ttk.Entry(main_frame, textvariable=self.take_profit_price_var).grid(row=4, column=1, sticky="EW", pady=4)

        ttk.Label(main_frame, text="Position Type").grid(row=5, column=0, sticky="W", pady=4)
        position_frame = ttk.Frame(main_frame)
        position_frame.grid(row=5, column=1, sticky="W", pady=4)
        ttk.Radiobutton(position_frame, text="Long", value="Long", variable=self.position_type).pack(side="left")
        ttk.Radiobutton(position_frame, text="Short", value="Short", variable=self.position_type).pack(side="left", padx=(8, 0))

        ttk.Label(main_frame, text="Instrument Type").grid(row=6, column=0, sticky="W", pady=4)
        instrument_combo = ttk.Combobox(
            main_frame,
            textvariable=self.instrument_type,
            values=("Crypto", "Forex"),
            state="readonly",
        )
        instrument_combo.grid(row=6, column=1, sticky="EW", pady=4)
        instrument_combo.bind("<<ComboboxSelected>>", lambda _event: self._set_currency_state())
        self.instrument_type.trace_add("write", lambda *_args: self._set_currency_state())

        ttk.Label(main_frame, text="Currency Pair (Forex)").grid(row=7, column=0, sticky="W", pady=4)
        self.currency_entry = ttk.Entry(main_frame, textvariable=self.currency_pair_var)
        self.currency_entry.grid(row=7, column=1, sticky="EW", pady=4)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, sticky="EW", pady=(8, 4))
        button_frame.columnconfigure(0, weight=1)
        ttk.Button(button_frame, text="Calculate", command=self.calculate).grid(row=0, column=0, sticky="EW")
        ttk.Button(button_frame, text="Clear", command=self._clear_form).grid(row=0, column=1, sticky="EW", padx=(8, 0))

        main_frame.rowconfigure(9, weight=1)
        self.result_text = tk.Text(main_frame, height=9, width=52, state="disabled", wrap="word")
        self.result_text.grid(row=9, column=0, columnspan=2, pady=(12, 0), sticky="NSEW")

    def calculate(self) -> None:
        """Triggered by the Calculate button; performs validation and updates the UI."""

        try:
            params = self._build_trade_parameters()
            metrics = calculate_trade_metrics(params)
            self._render_metrics(params, metrics)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))

    def _build_trade_parameters(self) -> TradeParameters:
        capital = self._parse_positive_float(self.capital_var.get(), "Total Capital (USD)")
        risk_percentage = self._parse_positive_float(self.risk_percentage_var.get(), "Risk per Trade (%)")
        entry_price = self._parse_positive_float(self.entry_price_var.get(), "Entry Price")
        stop_loss_price = self._parse_positive_float(self.stop_loss_price_var.get(), "Stop-Loss Price")
        take_profit_price = self._parse_optional_positive_float(
            self.take_profit_price_var.get(),
            "Take-Profit Price",
        )

        instrument_type = self.instrument_type.get()
        currency_pair: Optional[str] = None
        if instrument_type == "Forex":
            currency_pair = self.currency_pair_var.get().strip()

        return TradeParameters(
            capital=capital,
            risk_percentage=risk_percentage,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            position_type=self.position_type.get(),
            instrument_type=instrument_type,
            currency_pair=currency_pair or None,
        )

    def _render_metrics(self, params: TradeParameters, metrics: TradeMetrics) -> None:
        lines = [
            f"Risked Capital: ${metrics.risk_amount:,.2f}",
        ]

        if params.instrument_type == "Forex" and metrics.currency_pair:
            pip_size = get_pip_size(metrics.currency_pair)
            stop_loss_pips = metrics.stop_loss_distance / pip_size
            lines.append(
                f"Stop-Loss Distance: {metrics.stop_loss_distance:,.5f} "
                f"({stop_loss_pips:,.1f} pips)",
            )
            lines.append(f"Currency Pair: {metrics.currency_pair}")
            lines.append(f"Position Size: {metrics.position_size:,.4f} lots")
        else:
            lines.append(f"Stop-Loss Distance: {metrics.stop_loss_distance:,.6f}")
            lines.append(f"Position Size: {metrics.position_size:,.6f} units")

        if metrics.risk_reward_ratio is not None:
            lines.append(f"Risk-Reward Ratio: {metrics.risk_reward_ratio:.2f}")

        if metrics.potential_pnl is not None:
            lines.append(f"Potential P&L: ${metrics.potential_pnl:,.2f}")

        self._update_result_text("\n".join(lines))

    def _update_result_text(self, message: str) -> None:
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, message)
        self.result_text.configure(state="disabled")

    def _clear_form(self) -> None:
        self.capital_var.set("")
        self.risk_percentage_var.set("")
        self.entry_price_var.set("")
        self.stop_loss_price_var.set("")
        self.take_profit_price_var.set("")
        self.position_type.set("Long")
        self.instrument_type.set("Crypto")
        self.currency_pair_var.set("EUR/USD")
        self._set_currency_state()
        self._update_result_text("")

    def _set_currency_state(self) -> None:
        if self.instrument_type.get() == "Forex":
            self.currency_entry.state(["!disabled"])
        else:
            self.currency_entry.state(["disabled"])

    @staticmethod
    def _parse_positive_float(value: str, label: str) -> float:
        try:
            parsed = float(value)
        except ValueError as exc:
            raise ValueError(f"{label} must be a valid number.") from exc

        if parsed <= 0:
            raise ValueError(f"{label} must be greater than zero.")

        return parsed

    @staticmethod
    def _parse_optional_positive_float(value: str, label: str) -> Optional[float]:
        sanitized = value.strip()
        if not sanitized:
            return None

        try:
            parsed = float(sanitized)
        except ValueError as exc:
            raise ValueError(f"{label} must be a valid number.") from exc

        if parsed <= 0:
            raise ValueError(f"{label} must be greater than zero.")

        return parsed
