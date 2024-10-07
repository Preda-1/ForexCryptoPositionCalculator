# gui.py

import tkinter as tk
from tkinter import messagebox
from calculator import (
    calculate_risk_amount,
    calculate_distance,
    calculate_position_size,
    calculate_risk_reward_ratio,
    calculate_pnl,
)

class PositionCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Position Size Calculator")

        # Variables
        self.capital = tk.DoubleVar()
        self.risk_percentage = tk.DoubleVar()
        self.entry_price = tk.DoubleVar()
        self.stop_loss_price = tk.DoubleVar()
        self.take_profit_price = tk.DoubleVar()
        self.position_type = tk.StringVar(value="Long")
        self.instrument_type = tk.StringVar(value="Crypto")
        self.currency_pair = tk.StringVar(value="EUR/USD")

        # Create the GUI
        self.create_widgets()

    def create_widgets(self):
        # Labels and input fields
        tk.Label(self.root, text="Total Capital ($):").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.capital).grid(row=0, column=1)

        tk.Label(self.root, text="Risk per Trade (%):").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.risk_percentage).grid(row=1, column=1)

        tk.Label(self.root, text="Entry Price:").grid(row=2, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.entry_price).grid(row=2, column=1)

        tk.Label(self.root, text="Stop-Loss Price:").grid(row=3, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.stop_loss_price).grid(row=3, column=1)

        tk.Label(self.root, text="Take-Profit Price:").grid(row=4, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.take_profit_price).grid(row=4, column=1)

        tk.Label(self.root, text="Position Type:").grid(row=5, column=0, sticky=tk.W)
        tk.Radiobutton(self.root, text="Long", variable=self.position_type, value="Long").grid(row=5, column=1, sticky=tk.W)
        tk.Radiobutton(self.root, text="Short", variable=self.position_type, value="Short").grid(row=5, column=1, sticky=tk.E)

        tk.Label(self.root, text="Instrument Type:").grid(row=6, column=0, sticky=tk.W)
        tk.OptionMenu(self.root, self.instrument_type, "Crypto", "Forex").grid(row=6, column=1)

        tk.Label(self.root, text="Currency Pair (Forex):").grid(row=7, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.currency_pair).grid(row=7, column=1)

        # Calculate button
        tk.Button(self.root, text="Calculate", command=self.calculate).grid(row=8, column=0, columnspan=2, pady=10)

        # Results display
        self.result_text = tk.Text(self.root, height=10, width=50)
        self.result_text.grid(row=9, column=0, columnspan=2)

    def calculate(self):
        try:
            # Get user input
            capital = self.capital.get()
            risk_percentage = self.risk_percentage.get()
            entry_price = self.entry_price.get()
            stop_loss_price = self.stop_loss_price.get()
            take_profit_price = self.take_profit_price.get()
            position_type = self.position_type.get()
            instrument_type = self.instrument_type.get()
            currency_pair = self.currency_pair.get().upper()

            # Validate input
            if capital <= 0 or risk_percentage <= 0:
                raise ValueError("Capital and risk must be greater than zero.")

            if position_type not in ["Long", "Short"]:
                raise ValueError("Invalid position type selected.")

            if instrument_type not in ["Crypto", "Forex"]:
                raise ValueError("Invalid instrument type selected.")

            if instrument_type == "Forex" and not currency_pair:
                raise ValueError("Please enter a valid currency pair for Forex.")

            if instrument_type == "Forex" and not (currency_pair.endswith("USD") or currency_pair.startswith("USD")):
                raise ValueError("Currently, only currency pairs involving USD are supported.")

            # Adjust calculations based on position type
            if position_type == "Long" and stop_loss_price >= entry_price:
                raise ValueError("For long positions, stop-loss must be less than entry price.")
            if position_type == "Short" and stop_loss_price <= entry_price:
                raise ValueError("For short positions, stop-loss must be greater than entry price.")

            # Calculations
            risk_amount = calculate_risk_amount(capital, risk_percentage)
            distance = calculate_distance(entry_price, stop_loss_price)
            position_size = calculate_position_size(risk_amount, distance, instrument_type, entry_price, currency_pair)

            result = f"Risked Capital: ${risk_amount:.2f}\n"

            if instrument_type == "Forex":
                result += f"Position Size: {position_size:.4f} lots\n"
            else:
                result += f"Position Size: {position_size:.6f} units\n"

            if take_profit_price > 0:
                rr_ratio = calculate_risk_reward_ratio(entry_price, stop_loss_price, take_profit_price, position_type)
                pnl = calculate_pnl(entry_price, take_profit_price, position_size, position_type, instrument_type, currency_pair)
                result += f"Risk-Reward Ratio: {rr_ratio:.2f}\n"
                result += f"Potential P&L: ${pnl:.2f}\n"

            # Display results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)

        except Exception as e:
            messagebox.showerror("Error", str(e))
