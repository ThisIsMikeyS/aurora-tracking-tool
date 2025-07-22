# -*- coding: utf-8 -*-
"""
Main entry point for the Aurora Tracker GUI application.
"""

from gui import AuroraTrackerApp
import tkinter as tk


def main():
    root = tk.Tk()
    app = AuroraTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

