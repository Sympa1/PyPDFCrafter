import json
import os
from datetime import datetime
from pathlib import Path


class Utils:
    """Hilfsklasse für Konfiguration und Logging."""

    APP_NAME = "pdf_lab"

    def __init__(self):
        # Initialisiert Dateipfade und lädt beim Start die gespeicherte Konfiguration.
        # Ermittelt den Pfad zur Konfigurationsdatei:
        # Windows: C:\Users\<user>\AppData\Roaming\pdf_lab\config.json
        # Linux:   /home/<user>/.config/pdf_lab/config.json
        self.filename = self._get_config_dir() / "config.json"
        self.data = {}
        self.config_created = False
        self.load_config()

    @staticmethod
    def _get_config_dir() -> Path:
        """Gibt den plattformspezifischen Konfigurationsordner zurück und erstellt ihn falls nötig.

        Windows: C:\\Users\\<user>\\AppData\\Roaming\\pdf_lab\\
        Linux:   /home/<user>/.config/pdf_lab/
        """
        if os.name == "nt":  # Windows
            base = Path(os.environ["APPDATA"])
        else:  # Linux / macOS
            # XDG_CONFIG_HOME ist der Standard auf Linux; Fallback auf ~/.config
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

        # `Path`-Objekte nutzen `/` zum plattformunabhängigen Zusammenbauen von Pfaden.
        config_dir = base / Utils.APP_NAME
        config_dir.mkdir(parents=True, exist_ok=True)  # Ordner anlegen falls nicht vorhanden
        return config_dir

    @staticmethod
    def _get_log_dir() -> Path:
        """Gibt den plattformspezifischen Log-Ordner zurück und erstellt ihn falls nötig.

        Windows: C:\\Users\\<user>\\AppData\\Local\\pdf_lab\\logs\\
        Linux:   /home/<user>/.local/share/pdf_lab/logs/
        """
        if os.name == "nt":  # Windows
            base = Path(os.environ["LOCALAPPDATA"])
        else:  # Linux / macOS
            # XDG_DATA_HOME ist der Standard auf Linux; Fallback auf ~/.local/share
            base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

        # Logs werden pro App in einem eigenen Unterordner gesammelt.
        log_dir = base / Utils.APP_NAME / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)  # Ordner anlegen falls nicht vorhanden
        return log_dir

    @staticmethod
    def write_to_log(message: str, log_file_name: str = "error.log"):
        """Schreibt mit Zeitstempel eine Nachricht in die Log-Datei.

        Die Log-Datei liegt unter:
        Windows: C:\\Users\\<user>\\AppData\\Local\\pdf_lab\\logs\\error.log
        Linux:   /home/<user>/.local/share/pdf_lab/logs/error.log

        :param str message: Die zu protokollierende Nachricht.
        :param str log_file_name: Dateiname der Log-Datei, standardmäßig "error.log".
        """
        # Erlaubt auch alternative Logdateien, z. B. "debug.log".
        log_path = Utils._get_log_dir() / log_file_name
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {message}\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def load_config(self):
        """Liest die config.json ein. Wenn die Datei nicht existiert, wird eine neue mit Standardwerten erstellt."""
        try:
            # Lädt die vorhandene Konfiguration beim Start.
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError as e:
            # Standardwerte setzen, wenn noch keine Konfiguration vorhanden ist
            self.data = {
                "debug": False,
                "theme": "dark",
                "window_width": 1130,
                "window_height": 757,
            }
            # Erstellt die Datei direkt mit den Defaults, damit Folgezugriffe funktionieren.
            self.save_config()
            self.write_to_log("Config.json existiert nicht. " + str(e))
            self.config_created = True

    def save_config(self):
        """Speichert die aktuelle Konfiguration in der config.json."""
        # `indent=2` hält die Datei für manuelle Anpassungen lesbar.
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_config(self, key: str) -> int | str | bool | float | None:
        """Gibt den Wert für den angegebenen Schlüssel zurück, oder None, wenn der Schlüssel nicht existiert.

        :param str key: Der Schlüssel, dessen Wert abgerufen werden soll.
        :return int | str | bool | float | None: Der Wert für den angegebenen Schlüssel.
        """
        # `dict.get` liefert `None`, wenn der Schlüssel fehlt.
        return self.data.get(key)

    def set_config(self, key: str, value: str | int | bool):
        """Setzt den Wert für den angegebenen Schlüssel und speichert die config.json.
        """
        # Persistiert jede Änderung sofort, damit UI-Änderungen nicht verloren gehen.
        self.data[key] = value
        self.save_config()