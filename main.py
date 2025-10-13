"""Entry point for the Forex & Crypto Position Size Calculator application."""

from __future__ import annotations

import tkinter as tk

from gui import PositionCalculatorApp


def main() -> None:
    """Launch the Tkinter application."""

    root = tk.Tk()
    PositionCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
