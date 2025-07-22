# -*- coding: utf-8 -*-
"""
Graphical User Interface (GUI) implementation for the Aurora Tracker app.
Allows user to view KP index, aurora maps, solar data, forecasts, and webcam feeds.
"""

import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import ttk, messagebox
from matplotlib import dates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from aurora.aurora_map_overlay import generate_aurora_map
from aurora.kp_index import get_current_kp_index
from aurora.forecast import get_hourly_forecast, get_long_term_forecast, plot_3_day_forecast_chart, plot_long_term_forecast_chart
from aurora.swpc_map import download_swpc_map
from aurora.solar_data import download_sun_image, get_solar_wind_data, get_sun_image_urls
from aurora.webcams import get_live_webcams
from aurora.viewer_ranker import get_top_locations
from PIL import Image, ImageTk


class AuroraTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aurora Tracker")
        self.root.geometry("900x800")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.setup_kp_tab()
        self.setup_forecast_tab()
        self.setup_map_tab()
        self.setup_solar_tab()
        self.setup_sun_tab()
        self.setup_webcam_tab()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def _draw_forecast_chart(self, fig):
        """Embed matplotlib figure into forecast tab."""
        for widget in self.forecast_chart_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.forecast_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _draw_solar_charts(self, plasma_times, speeds, densities, mag_times, bz_values, bt_values):
        """
        Display four separate charts for solar wind data:
        - Speed (km/s)
        - Density (p/cc)
        - Bz (nT)
        - Bt (nT)
        """
        # Clear previous charts
        for widget in self.solar_chart_frame.winfo_children():
            widget.destroy()

        def embed_chart(title, times, values, ylabel):
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(times, values, color='red', linewidth=1.5)
            ax.set_title(title)
            ax.set_ylabel(ylabel)
            ax.set_xlabel("Time (UTC)")

            if len(times) >= 5:
                ax.set_xticks([
                    times[0],
                    times[len(times)//4],
                    times[len(times)//2],
                    times[3*len(times)//4],
                    times[-1]
                ])

            ax.tick_params(axis='x', rotation=45)
            ax.grid(True)
            fig.tight_layout()

            # Create a container frame that fills X but centers the graph inside it
            container = ttk.Frame(self.solar_chart_frame)
            container.pack(fill='x', pady=10)  # fill horizontally

            canvas = FigureCanvasTkAgg(fig, master=container)
            canvas.draw()
            canvas.get_tk_widget().pack(anchor='center')  # center inside the horizontal frame

        if plasma_times and speeds:
            embed_chart("Solar Wind Speeds (km/s)", plasma_times, speeds, "Speed (km/s)")

        if plasma_times and densities:
            embed_chart("Solar Wind Density (p/cc)", plasma_times, densities, "Density (p/cc)")

        if mag_times and bz_values:
            embed_chart("Solar Wind Bz (nT)", mag_times, bz_values, "Bz (nT)")

        if mag_times and bt_values:
            embed_chart("Solar Wind Bt (nT)", mag_times, bt_values, "Bt (nT)")

    def _load_sun_images_with_progress(self, urls, progress_bar):
        for index, (name, url) in enumerate(urls):
            path = download_sun_image(name, url)
            if not path or not path.exists():
                continue

            try:
                img = Image.open(path)
                img_resized = img.resize((400, 400))
                photo = ImageTk.PhotoImage(img_resized)
                self.sun_image_refs.append(photo)

                zoomed_img = img.resize((800, 800))
                zoomed_photo = ImageTk.PhotoImage(zoomed_img)
                self.sun_image_refs.append(zoomed_photo)

                frame = tk.Frame(self.sun_image_container, bg="#f0f0f0")
                frame.pack(pady=10)

                label = tk.Label(frame, image=photo)
                label.pack()

                caption = tk.Label(frame, text=name, font=("Arial", 10, "italic"))
                caption.pack()

                def on_enter(event, img=zoomed_photo, title=name):
                    if self.zoom_window is not None:
                        self.zoom_window.destroy()
                    self.zoom_window = tk.Toplevel()
                    self.zoom_window.title(f"Zoom: {title}")
                    self.zoom_window.geometry("+%d+%d" % (event.x_root + 20, event.y_root))
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

            # Update progress bar
            progress_bar["value"] = index + 1
            self.sun_image_container.update_idletasks()

        # Remove the progress bar after all images are loaded
        progress_bar.destroy()



    def on_tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        if tab_text == "KP Index & Visibility":
            self.show_aurora_overlay()

    def setup_kp_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="KP Index & Visibility")

        ttk.Label(tab, text="Current KP Index:", font=("Arial", 12)).pack(pady=5)
        self.kp_label = ttk.Label(tab, text="Loading...", font=("Arial", 16, "bold"))
        self.kp_label.pack()

        ttk.Button(tab, text="Refresh", command=self.update_kp_index).pack(pady=10)

        self.map_canvas = tk.Canvas(tab, width=750, height=567, bg="black")
        self.map_canvas.pack(pady=10)

        help_button = ttk.Button(tab, text="Help", command=self.show_map_help)
        help_button.pack(pady=5)

        self.update_kp_index()

    def update_kp_index(self):
        try:
            kp = round(get_current_kp_index(), 2)
            self.kp_label.config(text=str(kp))
            # locations = get_top_locations()
            # self.location_list.delete(0, tk.END)
            # for loc in locations:
            #     self.location_list.insert(tk.END, loc)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load KP index: {e}")

    def show_aurora_overlay(self):
        """Generates and displays the aurora forecast map."""
        try:
            path = generate_aurora_map()
            if path:
                img = Image.open(path)
                img = img.resize((750, 567), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.map_canvas.delete("all")
                self.map_canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
                self.map_canvas.image = tk_img  # Keep reference
            else:
                messagebox.showerror("Aurora Map", "Failed to generate aurora map.")
        except Exception as e:
            messagebox.showerror("Aurora Map Error", str(e))

    def show_map_help(self):
        help_text = (
            "🗺️ Aurora Map Overlay Help\n\n"
            "This map shows the probability of seeing the aurora based on NOAA's Ovation model.\n\n"
            "To maximise your changes of seeing the aurora, try to find an area with a red, orange or green colour, and without cloud coverage.\n\n"
            "Colour Legend:\n"
            "  🔴 Red: 50%+ chance of seeing aurora.\n"
            "  🟠 Orange: 30% to 49% chance of seeing aurora.\n"
            "  🟢 Green: 10% to 29% chance of seeing aurora.\n"
            "  ⚫ Dark Grey: 1% to 9%vchance of seeing aurora.\n\n"
            "The map updates dynamically using the latest space weather data."
        )
        messagebox.showinfo("Aurora Map Help", help_text)

    def setup_forecast_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Forecasts")

        ttk.Button(tab, text="Short-Term Forecast", command=self.show_hourly_forecast).pack(pady=10)
        ttk.Button(tab, text="Long-Term Forecast", command=self.show_long_forecast).pack(pady=10)

        self.forecast_chart_frame = ttk.Frame(tab)
        self.forecast_chart_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.forecast_chart_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')

    def show_hourly_forecast(self):
        """
        Fetch and display the 3-day Kp index forecast using a color-coded bar chart.
        Uses the 3_day_forecast_chart() utility for plotting.
        """
        try:
            dates, kp_values = get_hourly_forecast()

            if not dates or not kp_values:
                raise ValueError("No forecast data available.")

            plot_3_day_forecast_chart(self, dates, kp_values)

        except Exception as e:
            messagebox.showerror("Short-Term Forecast Error", f"Failed to load forecast: {e}")

    def show_long_forecast(self):
        """
        Fetch and display the 27-day Kp index forecast using a color-coded bar chart.
        Uses the plot_long_term_forecast_chart() utility for plotting.
        """
        try:
            dates, kp_values = get_long_term_forecast()

            if not dates or not kp_values:
                raise ValueError("No forecast data available.")

            plot_long_term_forecast_chart(self, dates, kp_values)

        except Exception as e:
            messagebox.showerror("Long-Term Forecast Error", f"Failed to load forecast: {e}")



    def setup_map_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Aurora Map")

        ttk.Button(tab, text="Download Latest Map", command=self.display_map).pack(pady=10)
        self.map_label = ttk.Label(tab)
        self.map_label.pack()

    def display_map(self):
        try:
            path = download_swpc_map()
            img = Image.open(path).resize((600, 600))
            self.map_img = ImageTk.PhotoImage(img)
            self.map_label.config(image=self.map_img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map: {e}")

    def setup_solar_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Solar Data")

        ttk.Button(tab, text="Fetch Solar Wind Data", command=self.show_solar_wind_graphs).pack(pady=10)

        # Create a canvas and a scrollable frame
        canvas = tk.Canvas(tab, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.solar_chart_frame = ttk.Frame(canvas)
    
        # Bind frame resizing to canvas size
        self.solar_chart_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Allow the internal frame to match the width of the canvas
        window = canvas.create_window((0, 0), window=self.solar_chart_frame, anchor="nw")

        # Stretch inner frame width with canvas
        def resize_frame(event):
            canvas.itemconfig(window, width=event.width)
        canvas.bind("<Configure>", resize_frame)

        # Mousewheel scroll — bind only while hovering
        def on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def on_leave(event):
            canvas.unbind_all("<MouseWheel>")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

    def display_solar_data(self):
        data = get_solar_wind_data()
        self.solar_text.delete("1.0", tk.END)
        for k, v in data.items():
            self.solar_text.insert(tk.END, f"{k}: {v}\n")

    def show_solar_wind_graphs(self):
        """Fetch and render solar wind line charts."""
        try:
            plasma_times, speeds, densities, mag_times, bz_values, bt_values = get_solar_wind_data()

            if not plasma_times or not mag_times:
                raise ValueError("Could not retrieve solar data.")

            self._draw_solar_charts(plasma_times, speeds, densities, mag_times, bz_values, bt_values)

        except Exception as e:
            messagebox.showerror("Solar Data Error", f"Failed to load solar wind data: {e}")

    def setup_sun_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sun Images")

        ttk.Button(tab, text="Show Sun Images", command=self.display_sun_images).pack(pady=10)

        # Create scrollable canvas
        canvas = tk.Canvas(tab, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.sun_image_container = ttk.Frame(canvas)
        self.sun_image_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Center inside canvas
        window = canvas.create_window((0, 0), window=self.sun_image_container, anchor="n")

        def resize_frame(event):
            canvas.itemconfig(window, width=event.width)
        canvas.bind("<Configure>", resize_frame)

        # Mousewheel scroll — bind only while hovering
        def on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def on_leave(event):
            canvas.unbind_all("<MouseWheel>")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)


    def display_sun_image(self):
        try:
            img_path = download_sun_image()
            img = Image.open(img_path).resize((400, 400))
            self.sun_img = ImageTk.PhotoImage(img)
            self.sun_label.config(image=self.sun_img)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load sun image: {e}")

    def display_sun_images(self):
        urls = get_sun_image_urls()

        # Clear old images
        for widget in self.sun_image_container.winfo_children():
            widget.destroy()

        self.sun_image_refs = []
        self.zoom_window = None

        # Create and pack the progress bar
        progress = ttk.Progressbar(self.sun_image_container, mode='determinate', length=400)
        progress.pack(pady=20)
        progress["maximum"] = len(urls)
        progress["value"] = 0

        self.sun_image_container.update_idletasks()

        # Delay processing to allow UI to draw progress bar
        self.root.after(100, lambda: self._load_sun_images_with_progress(urls, progress))



    def setup_webcam_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Aurora Webcams")

        ttk.Label(tab, text="Click a webcam to view live:").pack()
        self.webcam_list = tk.Listbox(tab, height=15)
        self.webcam_list.pack(fill=tk.BOTH, expand=True)
        ttk.Button(tab, text="Open Webcam", command=self.open_webcam).pack(pady=10)

        cams = get_live_webcams()
        for cam in cams:
            location = cam.get("location")
            url = cam.get("url")
            self.webcam_list.insert(tk.END, f"{location}:           {url}")

    def open_webcam(self):
        sel = self.webcam_list.curselection()
        if sel:
            entry = self.webcam_list.get(sel[0])
            _, url = entry.split(":           ")
            webbrowser.open(url)