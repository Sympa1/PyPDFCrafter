# PDF Lab

PDF Lab ist ein Desktop-Tool zum Bearbeiten von PDF-Dateien. Es läuft auf Windows und Linux.

## Funktionen
- **PDF mergen** – Mehrere PDFs zu einer Datei zusammenführen
- **PDF splitten** – Eine PDF an einer gewählten Seite in zwei Teile aufteilen
- **PDF ver- und entschlüsseln** – PDFs mit Passwort schützen oder entsperren
- **Passwortstärke-Anzeige** – Echtzeit-Feedback mit Fortschrittsbalken und Kriteriencheckliste
- **Dark-/Lightmode** – Theme-Wechsel per Knopfdruck, wird gespeichert
- **Einstellungen persistent** – Fenstergröße und Theme bleiben nach Neustart erhalten
- **Plattformgerechte Dateispeicherung** – Konfiguration und Log werden im Benutzerordner abgelegt (XDG-Standard auf Linux, AppData auf Windows)

## Speicherorte der Programmdateien
| Datei | Windows | Linux |
|---|---|---|
| Konfiguration | `%APPDATA%\pdf_lab\config.json` | `~/.config/pdf_lab/config.json` |
| Log | `%LOCALAPPDATA%\pdf_lab\logs\error.log` | `~/.local/share/pdf_lab/logs/error.log` |

## Lessons Learned
Eine kleine Herausforderung war es für mich das UI zu gestalten. CustomTkinter bietet aber gute Möglichkeiten ein modernes UI zu gestalten.
Eine größere Herausforderung, weil ich das noch nicht gemacht habe, war es, die Settings (Fenstergröße und Theme) nachhaltig zu speichern. Die Möglichkeit wollte ich möglichst simpel halten, was mir auch gelungen ist. Im Großen und Ganzen habe ich einiges dazu gelernt und daher bewerte ich das Projekt als Erfolg.

## Voraussetzungen
- Python 3.10+
- pip
- virtualenv (empfohlen)

## Verzeichnisstruktur
```
.
├── data/
│   └── img/
│       ├── icon.ico
│       ├── icon.png
│       └── ...
├── src/
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── cl_Gui.py
│   │   ├── cl_TabView.py
│   │   ├── cl_TabMergen.py
│   │   ├── cl_TabSplitten.py
│   │   ├── cl_TabVerschluesseln.py
│   │   ├── cl_Theme.py
│   │   └── cl_Messagebox.py
│   ├── classes/
│   │   ├── __init__.py
│   │   ├── cl_PdfUtility.py
│   │   └── cl_Utils.py
│   └── main.py
├── tests/
├── .venv/
├── .gitignore
├── pdf_lab.desktop
├── LICENSE
├── README.md
├── requirements.txt
└── starter.sh
```

## Installation
1. Dieses Repository klonen:
   ```
   git clone https://github.com/Sympa1/pdf_lab
   ```
2. In das Repository-Verzeichnis navigieren:
   ```
   cd pdf_lab
   ```
3. Virtuelles Environment einrichten:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
5. App starten:
   ```bash
   ./starter.sh        # Linux
   python src/main.py  # Windows
   ```

## Linux: App im Launcher registrieren
```bash
cp pdf_lab.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## AppImage erstellen (Linux)

Ein AppImage ist eine portable Datei die auf jeder Linux-Distribution ohne Installation läuft.

### Voraussetzungen

```bash
# PyInstaller installieren (falls noch nicht vorhanden)
pip install pyinstaller

# appimagetool herunterladen
wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

### Schritt 1 – PyInstaller-Build erstellen

```bash
pyinstaller --onedir --windowed \
  --name "PDFLab" \
  --icon=data/img/icon.ico \
  --hidden-import=customtkinter \
  --hidden-import=PIL._tkinter_finder \
  --add-data "data/img:data/img" \
  src/main.py
```

> Erzeugt den Ordner `dist/PDFLab/` mit allen nötigen Dateien.

### Schritt 2 – AppDir-Struktur anlegen

```bash
mkdir -p PDFLab.AppDir/usr/bin
mkdir -p PDFLab.AppDir/usr/share/icons

# PyInstaller-Output in AppDir kopieren
cp -r dist/PDFLab/* PDFLab.AppDir/usr/bin/

# Icon und .desktop-Datei in AppDir legen
cp data/img/icon.png PDFLab.AppDir/pdf_lab.png
cp pdf_lab.desktop PDFLab.AppDir/pdf_lab.desktop
```

### Schritt 3 – AppRun-Datei erstellen

```bash
cat > PDFLab.AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/PDFLab" "$@"
EOF
chmod +x PDFLab.AppDir/AppRun
```

### Schritt 4 – AppImage bauen

```bash
./appimagetool-x86_64.AppImage PDFLab.AppDir PDFLab.AppImage
```

> Die fertige Datei `PDFLab.AppImage` kann direkt ausgeführt werden:
> ```bash
> chmod +x PDFLab.AppImage
> ./PDFLab.AppImage
> ```

### Hinweis
Build-Artefakte (`dist/`, `build/`, `*.AppImage`, `*.AppDir`) sind in `.gitignore` eingetragen und werden nicht ins Repository hochgeladen.


- Unter Wayland wird das Fenster-Icon nicht über `iconphoto()` angezeigt – das Icon erscheint korrekt wenn die App über die `.desktop`-Datei gestartet wird

## Build-Tools
- PyInstaller 6.1.0
```shell
pyinstaller --onefile --windowed --icon=data/img/icon.ico --hidden-import=customtkinter --add-data "data/img;data/img" src/main.py
```

## Lizenz
Dieses Projekt ist unter der GPL-3.0 lizenziert - siehe die [LICENSE](LICENSE)-Datei für Details.
