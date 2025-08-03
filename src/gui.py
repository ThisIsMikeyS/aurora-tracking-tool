# -*- coding: utf-8 -*-
"""
Aurora Tracker - GUI Interface
Provides a multi-tab Tkinter interface to view KP index, aurora maps,
solar data, forecasts, and webcams, with a dark theme applied.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

# Aurora Tracker modules
from aurora.aurora_map_overlay import generate_aurora_map
from aurora.kp_index import get_current_kp_index
from aurora.forecast import (
    get_hourly_forecast,
    get_long_term_forecast,
    plot_3_day_forecast_chart,
    plot_long_term_forecast_chart
)
from aurora.swpc_map import download_swpc_map
from aurora.solar_data import download_sun_image, get_solar_wind_data, get_sun_image_urls
from aurora.webcams import get_live_webcams_best_sorted
from config import UISettings, OVERLAY_MAP_INFO, WEBCAM_TAB_INFO


class AuroraTrackerApp:
    """Main GUI application for Aurora Tracker."""

    def __init__(self, root):
        self.root = root
        self.root.title(UISettings.WINDOW_TITLE)
        self.root.geometry(UISettings.WINDOW_SIZE)

        # Set custom icon (Windows ICO)
        self._set_app_icon()

        # Apply dark mode theme
        self._apply_dark_theme()

        # Create main tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize tabs
        self.setup_kp_tab()
        self.setup_forecast_tab()
        # self.setup_map_tab()  # Optional tab
        self.setup_solar_tab()
        self.setup_sun_tab()
        self.setup_webcam_tab()

        # Bind tab change events
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    # =========================
    #  UI INITIALIZATION
    # =========================

    def _set_app_icon(self):
        """Sets the application icon (Windows ICO if available)."""
        icon_path = os.path.join("assets", "icons", "aurora_tracker_icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

    def _apply_dark_theme(self):
        """Configures a dark mode theme for the entire UI."""
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".",
                        background=UISettings.DARK_THEME_BG,
                        foreground=UISettings.DARK_THEME_FG,
                        fieldbackground=UISettings.DARK_THEME_BG)

        style.configure("TNotebook", background=UISettings.DARK_THEME_BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=UISettings.DARK_THEME_ACCENT,
                        foreground=UISettings.DARK_THEME_FG)
        style.map("TNotebook.Tab",
                  background=[("selected", UISettings.DARK_THEME_BG)],
                  foreground=[("selected", UISettings.DARK_THEME_FG)])

        style.configure("TLabel", background=UISettings.DARK_THEME_BG, foreground=UISettings.DARK_THEME_FG)
        style.configure("TButton", background=UISettings.DARK_THEME_ACCENT, foreground=UISettings.DARK_THEME_FG)
        style.map("TButton", background=[("active", "#3a4b63")])

        self.root.configure(bg=UISettings.DARK_THEME_BG)

    # =========================
    #  TAB: KP INDEX & MAP
    # =========================

    def setup_kp_tab(self):
        """Initializes KP Index & Aurora Map tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="KP Index & Visibility")

        ttk.Label(tab, text="Current KP Index:", font=("Arial", 12)).pack(pady=5)
        self.kp_label = ttk.Label(tab, text="Loading...", font=("Arial", 16, "bold"))
        self.kp_label.pack()

        ttk.Button(tab, text="Refresh", command=self.refresh_kp_and_map).pack(pady=10)

        self.map_canvas = tk.Canvas(tab, width=750, height=567, bg="black")
        self.map_canvas.pack(pady=10)

        ttk.Button(tab, text="Help", command=self.show_map_help).pack(pady=5)

        self.update_kp_index()  # Load initial KP value

    def refresh_kp_and_map(self):
        """Refreshes both KP index and aurora overlay."""
        self.update_kp_index()
        self.show_aurora_overlay()

    def update_kp_index(self):
        """Fetches current KP index and updates label."""
        try:
            kp = round(get_current_kp_index(), 2)
            self.kp_label.config(text=str(kp))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load KP index: {e}")

    def show_aurora_overlay(self):
        """Generates and displays the aurora forecast overlay map."""
        try:
            path = generate_aurora_map()
            if path:
                img = Image.open(path).resize((750, 567), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.map_canvas.delete("all")
                self.map_canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
                self.map_canvas.image = tk_img  # Keep reference
            else:
                messagebox.showerror("Aurora Map", "Failed to generate aurora map.")
        except Exception as e:
            messagebox.showerror("Aurora Map Error", str(e))

    def show_map_help(self):
        """Displays help dialog for the aurora overlay map."""
        messagebox.showinfo("Aurora Map Help", OVERLAY_MAP_INFO)

    # =========================
    #  TAB: FORECASTS
    # =========================

    def setup_forecast_tab(self):
        """Initializes Forecast tab (short-term and long-term)."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Forecasts")

        ttk.Button(tab, text="Short-Term Forecast", command=self.show_hourly_forecast).pack(pady=10)
        ttk.Button(tab, text="Long-Term Forecast", command=self.show_long_forecast).pack(pady=10)

        self.forecast_chart_frame = ttk.Frame(tab)
        self.forecast_chart_frame.pack(fill=tk.BOTH, expand=True)

    def _draw_forecast_chart(self, fig):
        """Embeds a forecast matplotlib figure into the forecast tab."""
        for widget in self.forecast_chart_frame.winfo_children():
            widget.destroy()

        fig.tight_layout(pad=2.0)
        container = ttk.Frame(self.forecast_chart_frame)
        container.pack(fill='x', pady=1)

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(anchor='center')

        plt.close(fig)  # Prevent figure memory leak

    def show_hourly_forecast(self):
        """Displays short-term (3-day) forecast."""
        try:
            dates, kp_values = get_hourly_forecast()
            if not dates or not kp_values:
                raise ValueError("No forecast data available.")
            plot_3_day_forecast_chart(self, dates, kp_values)
        except Exception as e:
            messagebox.showerror("Short-Term Forecast Error", f"Failed to load forecast: {e}")

    def show_long_forecast(self):
        """Displays long-term (27-day) forecast."""
        try:
            dates, kp_values = get_long_term_forecast()
            if not dates or not kp_values:
                raise ValueError("No forecast data available.")
            plot_long_term_forecast_chart(self, dates, kp_values)
        except Exception as e:
            messagebox.showerror("Long-Term Forecast Error", f"Failed to load forecast: {e}")

    # =========================
    #  TAB: SOLAR DATA
    # =========================

    def setup_solar_tab(self):
        """Initializes Solar Data tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Solar Data")

        ttk.Button(tab, text="Fetch Solar Wind Data", command=self.show_solar_wind_graphs).pack(pady=10)

        # Scrollable chart frame
        canvas = tk.Canvas(tab, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.solar_chart_frame = ttk.Frame(canvas)
        self.solar_chart_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((0, 0), window=self.solar_chart_frame, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    def _draw_solar_charts(self, plasma_times, speeds, densities, mag_times, bz_values, bt_values):
        """Plots multiple solar wind charts."""
        for widget in self.solar_chart_frame.winfo_children():
            widget.destroy()

        def embed_chart(title, times, values, ylabel):
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(times, values, color='red', linewidth=1.5)
            ax.set_title(title)
            ax.set_ylabel(ylabel)
            ax.set_xlabel("Time (UTC)")
            if len(times) >= 5:
                ax.set_xticks([times[0], times[len(times)//4], times[len(times)//2], times[3*len(times)//4], times[-1]])
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True)
            fig.tight_layout()

            container = ttk.Frame(self.solar_chart_frame)
            container.pack(fill='x', pady=10)
            canvas = FigureCanvasTkAgg(fig, master=container)
            canvas.draw()
            canvas.get_tk_widget().pack(anchor='center')

        if plasma_times and speeds: embed_chart("Solar Wind Speeds (km/s)", plasma_times, speeds, "Speed (km/s)")
        if plasma_times and densities: embed_chart("Solar Wind Density (p/cc)", plasma_times, densities, "Density (p/cc)")
        if mag_times and bz_values: embed_chart("Solar Wind Bz (nT)", mag_times, bz_values, "Bz (nT)")
        if mag_times and bt_values: embed_chart("Solar Wind Bt (nT)", mag_times, bt_values, "Bt (nT)")

    def show_solar_wind_graphs(self):
        """Fetches and displays solar wind charts."""
        try:
            plasma_times, speeds, densities, mag_times, bz_values, bt_values = get_solar_wind_data()
            if not plasma_times or not mag_times:
                raise ValueError("Could not retrieve solar data.")
            self._draw_solar_charts(plasma_times, speeds, densities, mag_times, bz_values, bt_values)
        except Exception as e:
            messagebox.showerror("Solar Data Error", f"Failed to load solar wind data: {e}")

    # =========================
    #  TAB: SUN IMAGES
    # =========================

    def setup_sun_tab(self):
        """Initializes Sun Images tab with scrollable container."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sun Images")

        # Button to load sun images
        self.show_sun_button = ttk.Button(tab, text="Show Sun Images", command=self.display_sun_images)
        self.show_sun_button.pack(pady=10)

        # Scrollable canvas for images
        canvas = tk.Canvas(tab, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.sun_image_container = ttk.Frame(canvas)
        self.sun_image_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        window = canvas.create_window((0, 0), window=self.sun_image_container, anchor="n")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window, width=e.width))
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    def display_sun_images(self):
        """Triggers threaded loading of sun images with progress bar."""
        urls = get_sun_image_urls()

        # Clear previous images
        for widget in self.sun_image_container.winfo_children():
            widget.destroy()

        self.sun_image_refs = []
        self.zoom_window = None

        # Disable button to prevent multiple clicks
        self.show_sun_button.config(state="disabled")

        # Progress bar for loading
        progress_bar = ttk.Progressbar(self.sun_image_container, mode='determinate', length=400)
        progress_bar.pack(pady=20)
        progress_bar["maximum"] = len(urls)
        progress_bar["value"] = 0

        self.sun_image_container.update_idletasks()

        # Start threaded loading
        threading.Thread(target=self._load_images_thread, args=(urls, progress_bar), daemon=True).start()

    def _load_images_thread(self, urls, progress):
        """Background thread for loading sun images."""
        for index, (name, url) in enumerate(urls):
            path = download_sun_image(name, url)
            if path and path.exists():
                self.root.after(0, lambda p=path, n=name: self._add_sun_image(p, n))
            self.root.after(0, lambda v=index + 1: progress.config(value=v))

        # Re-enable button and remove progress bar when done
        self.root.after(0, lambda: self.show_sun_button.config(state="normal"))
        self.root.after(0, progress.destroy)

    def _add_sun_image(self, path, name):
        """Adds image with hover zoom to UI (runs on main thread)."""
        try:
            # Main image
            img = Image.open(path).resize((400, 400))
            photo = ImageTk.PhotoImage(img)
            self.sun_image_refs.append(photo)

            # Zoomed image
            zoomed_img = img.resize((800, 800))
            zoomed_photo = ImageTk.PhotoImage(zoomed_img)
            self.sun_image_refs.append(zoomed_photo)

            # Frame for image + caption
            frame = tk.Frame(self.sun_image_container, bg="#f0f0f0")
            frame.pack(pady=10)

            label = tk.Label(frame, image=photo)
            label.pack()

            caption = tk.Label(frame, text=name, font=("Arial", 10, "italic"))
            caption.pack()

            # Hover zoom handlers
            def on_enter(event, img=zoomed_photo, title=name):
                if self.zoom_window is not None:
                    self.zoom_window.destroy()
                self.zoom_window = tk.Toplevel()
                self.zoom_window.title(f"Zoom: {title}")
                self.zoom_window.geometry(f"+{event.x_root + 20}+{event.y_root}")
                self.zoom_window.overrideredirect(True)
                zoom_label = tk.Label(self.zoom_window, image=img)
                zoom_label.pack()

            def on_leave(event):
                if self.zoom_window:
                    self.zoom_window.destroy()
                    self.zoom_window = None

            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)

        except Exception as e:
            print(f"[ERROR] Could not load image {name}: {e}")

    # =========================
    #  TAB: WEBCAMS
    # =========================

    def setup_webcam_tab(self):
        """Initializes Aurora Webcams tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Aurora Webcams")

        ttk.Label(tab, text="Click a webcam to view live:").pack()
        self.webcam_list = tk.Listbox(tab, height=15)
        self.webcam_list.pack(fill=tk.BOTH, expand=True)
        ttk.Button(tab, text="Open Webcam", command=self.open_webcam).pack(pady=10)

        # Populate webcam list
        cams = get_live_webcams_best_sorted()
        self.webcam_url_map = {}
        for cam in cams:
            location = cam.get("location")
            country = cam.get("country")
            url = cam.get("url")
            if location and url:
                entry = f"{location}, {country}"
                self.webcam_list.insert(tk.END, entry)
                self.webcam_url_map[entry] = url

        ttk.Button(tab, text="Help", command=self.show_webcams_help).pack(pady=5)

    def open_webcam(self):
        """Opens the selected webcam in the default browser."""
        sel = self.webcam_list.curselection()
        if sel:
            location = self.webcam_list.get(sel[0])
            url = self.webcam_url_map.get(location)
            if url:
                webbrowser.open(url)
            else:
                messagebox.showerror("Webcam Error", f"No URL found for {location}")

    def show_webcams_help(self):
        """Displays help information for webcam tab."""
        messagebox.showinfo("Aurora Webcams Help", WEBCAM_TAB_INFO)

    # =========================
    #  TAB CHANGE EVENT
    # =========================

    def on_tab_changed(self, event):
        """Handles actions when switching between tabs."""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        if tab_text == "KP Index & Visibility":
            self.show_aurora_overlay()

