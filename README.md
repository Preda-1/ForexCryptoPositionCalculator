# Forex & Crypto Position Size Calculator

A polished Python project that helps traders size their positions responsibly across
both Forex and crypto markets. The application combines a tested calculation engine
with a friendly Tkinter interface, making it easy to visualise risk, position size,
risk/reward ratios, and projected P&L before entering a trade.

## Features
- Accurate risk-based position sizing for **Forex** (in lots) and **crypto** (in units).
- Comprehensive validation to prevent common configuration mistakes.
- Normalisation of currency pairs with pip value support for all USD crosses.
- Modernised Tkinter GUI with instant feedback and optional take-profit analysis.
- Automated unit tests covering the calculation layer for confidence when iterating.

## Project Structure
```text
.
├── calculator.py          # Core calculation logic and validation utilities
├── gui.py                 # Tkinter desktop interface
├── main.py                # Application entry point
├── tests/
│   └── test_calculator.py # Pytest suite for the calculation engine
├── requirements-dev.txt   # Development-only dependencies
└── README.md              # Project documentation
```

## Getting Started

> Python 3.10+ is recommended. The runtime application has no third-party dependencies;
> `pytest` is only required when you want to execute the test-suite.

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ForexCryptoPositionCalculator.git
cd ForexCryptoPositionCalculator

# 2. (Optional) Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install development dependencies if you plan to run the tests
pip install -r requirements-dev.txt
```

## Running the Application

```bash
python main.py
```

The window prompts you for:
- Account capital and preferred risk percentage
- Entry, stop-loss, and optional take-profit prices
- Position direction (long/short) and instrument type
- Normalised USD currency pair when working with Forex

Calculated metrics include risked capital, stop-loss distance, position size, risk/reward
ratio, and potential profit at the specified target.

## Running the Tests

```bash
python -m pytest
```

The test-suite focuses on the calculation layer, validating pip-value math, distance
checks, and the higher-level trade metric aggregation.

## Extending the Project
- Add additional account currencies by extending `SUPPORTED_ACCOUNT_CURRENCIES` and wiring
  in the relevant FX conversion logic.
- Persist historical scenarios or Monte-Carlo simulations using the calculation engine.
- Swap out Tkinter for a web or CLI layer if you want to deploy the tool remotely.

## Security & Privacy
- The repository intentionally avoids storing API keys, credentials, or live broker data.
- User input never leaves the local machine; nothing is logged or transmitted.
- Make sure to review your commit history before making the repository public.

## Contributing
Contributions are welcome—open an issue or submit a pull request with improvements.
Before submitting changes, run the tests to keep the main branch green.

## License
Add the licence that best matches how you intend others to use this repository (e.g. MIT,
Apache 2.0). Remember to include the dedicated `LICENSE` file before going public.
