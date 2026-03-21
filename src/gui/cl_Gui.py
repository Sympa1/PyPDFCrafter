import customtkinter as ctk
from PIL import Image, ImageTk
import os

from .cl_TabView import TabView
from .cl_Theme import Theme
from .cl_Messagebox import Messagebox
from classes import Utils



class Gui(ctk.CTk):  
    def __init__(self):
        super().__init__()
        self.title("PDF Lab")

        # Grid-Konfiguration direkt nach Fenster-Setup
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.config = Utils()

        # Fenstergröße aus Config laden
        self.window_width = self.config.get_config("window_width")
        self.window_height = self.config.get_config("window_height")
        self.geometry(f"{self.window_width}x{self.window_height}")

        # Icon setzen nachdem Fenster und Größe initialisiert sind
        self._set_icon()

        # Theme - default Darkemode
        self.theme_status = f"{self.config.get_config("theme")}"
        ctk.set_appearance_mode(self.theme_status)

        # Top-Bar Frame in Zeile 0 – nimmt die volle Breite ein
        # Enthält links den Info-Button und rechts den Theme-Switch
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        # Info-Button links in der Top-Bar – zeigt Speicherorte von Config und Log
        self.info_button = ctk.CTkButton(
            self.top_bar,
            text="Speicherort Programmdateien",
            width=220,
            command=self.show_storage_info
        )
        self.info_button.pack(side="left")

        # Theme-Switch rechts in der Top-Bar
        self.theme_frame = Theme(self.top_bar, self.config)
        self.theme_frame.pack(side="right")

        # TabView direkt darunter in Zeile 1, Spalte 0
        self.tabview = TabView(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="nsew")

        self.button = ctk.CTkButton(self, text="Beenden", hover=True, width=20, command=self.on_close)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="se")

        # Nach dem Aufbau prüfen ob config neu erstellt wurde
        self.after(100, self.check_config_created)

        # Event-Handler für das Schließen des Fensters setzen
        # Speichert die aktuelle Fenstergröße in der Config beim Beenden
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _set_icon(self):
        """Setzt das Anwendungssymbol für Titelleiste und Taskleiste.
        Sucht zuerst nach einer .ico-Datei (Windows), dann nach einer .png-Datei (Linux/macOS).
        Wird kein Icon gefunden, startet die App ohne Symbol.
        """
        # Pfad zum img-Ordner relativ zu dieser Datei ermitteln
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "img")

        ico_path = os.path.join(assets_dir, "icon.ico")
        png_path = os.path.join(assets_dir, "icon.png")

        try:
            if os.path.exists(ico_path):
                # .ico bevorzugt auf Windows – beste Taskleisten-Unterstützung
                self.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                # .png als Fallback für Linux / macOS
                icon = ImageTk.PhotoImage(Image.open(png_path))
                self.iconphoto(True, icon)  # True = Icon gilt auch für alle Unterfenster
        except Exception:
            pass  # App startet ohne Icon falls ein Fehler auftritt

    def show_storage_info(self):
        """Zeigt eine Messagebox mit den plattformspezifischen Speicherorten
        für Konfiguration und Log-Dateien an.
        """
        config_path = Utils._get_config_dir() / "config.json"
        log_path = Utils._get_log_dir() / "error.log"

        Messagebox(
            "Speicherorte",
            f"Konfiguration:\n{config_path}\n\nLog-Datei:\n{log_path}"
        ).messagebox_info()

    def check_config_created(self):
        """Prüft, ob die Konfigurationsdatei erstellt wurde und zeigt eine Info-Messagebox an.
        """

        if getattr(self.config, "config_created", False):
            Messagebox("Info", "Die Konfigurationsdatei 'config.json' wurde nicht gefunden. Standardwerte wurden gesetzt.").messagebox_info()

    def on_close(self):
        """Wird beim Schließen des Fensters aufgerufen. Speichert die aktuelle Fenstergröße.
        """
        
        width = self.winfo_width()
        height = self.winfo_height()
        self.config.set_config("window_width", width)
        self.config.set_config("window_height", height)
        self.destroy()