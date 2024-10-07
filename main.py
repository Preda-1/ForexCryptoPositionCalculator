# main.py

import tkinter as tk
from gui import PositionCalculatorApp

def main():
    root = tk.Tk()
    app = PositionCalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
