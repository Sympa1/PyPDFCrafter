import customtkinter as ctk
from tkinter import filedialog
import os
from classes.cl_PdfUtility import PdfUtility
from .cl_Messagebox import Messagebox
from classes.cl_Utils import Utils

# TODO: ich brauche einen "reset" der PDF Liste nach einem splitten per Button
# TODO: eine Progressbar für den split Prozess

class TabSplitten(ctk.CTkFrame):
    """
    Tab-Klasse für das Splitten von PDF-Dateien.
    Erbt von ctk.CTkFrame und stellt die GUI-Komponenten für die PDF-Split-Funktionalität bereit.
    """

    def __init__(self, master):
        super().__init__(master)
        self.input_pdf = None  # Pfad zur aktuell ausgewählten PDF-Datei
        self.output_part1 = None  # Pfad für den ersten Teil der gesplitteten PDF
        self.output_part2 = None  # Pfad für den zweiten Teil der gesplitteten PDF
        self.pdf_utility = PdfUtility()  # Utility-Objekt für PDF-Operationen

        # Spalte 0 dehnt sich mit der Fensterbreite aus
        self.grid_columnconfigure(0, weight=1)

        # === GUI-ELEMENTE ERSTELLEN ===

        # Button zum Auswählen der zu splittenden PDF-Datei – zentriert
        self.select_file_button = ctk.CTkButton(self, text="PDF zum Splitten auswählen", command=self.select_input_pdf)
        self.select_file_button.grid(row=0, column=0, padx=20, pady=(20, 0))

        # Label zur Anzeige der aktuell ausgewählten PDF-Datei
        self.file_label = ctk.CTkLabel(self, text="Keine Datei ausgewählt")
        self.file_label.grid(row=1, column=0, padx=20, pady=(5, 0))

        # Label zur Anzeige der Seitenanzahl der ausgewählten PDF
        self.page_info_label = ctk.CTkLabel(self, text="")
        self.page_info_label.grid(row=2, column=0, padx=20, pady=(5, 0))

        # Frame für die Spinbox (Seitenzahl zum Splitten) – zentriert
        self.spinbox_frame = ctk.CTkFrame(self)
        self.spinbox_frame.grid(row=3, column=0, padx=20, pady=(10, 0))

        # Label für die Spinbox
        self.spinbox_label = ctk.CTkLabel(self.spinbox_frame, text="Splitten nach Seite:")
        self.spinbox_label.pack(side="left", padx=(10, 5), pady=10)

        # Custom Spinbox mit - Button, Entry und + Button
        self.minus_button = ctk.CTkButton(self.spinbox_frame, text="-", width=30, command=self.decrease_value)
        self.minus_button.pack(side="left", padx=2, pady=10)

        # Eingabefeld für die Seitenzahl, an der gesplittet werden soll
        self.page_entry = ctk.CTkEntry(self.spinbox_frame, width=60, justify="center")
        self.page_entry.pack(side="left", padx=2, pady=10)
        self.page_entry.insert(0, "1")
        self.page_entry.bind("<KeyRelease>", self.validate_page_number)

        self.plus_button = ctk.CTkButton(self.spinbox_frame, text="+", width=30, command=self.increase_value)
        self.plus_button.pack(side="left", padx=2, pady=10)

        # Frame für die Anzeige und Auswahl der Output-Pfade – dehnt sich horizontal aus
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        # Label und Button für Output Teil 1
        self.output1_label = ctk.CTkLabel(self.output_frame, text="Output Teil 1: Standardpfad wird verwendet")
        self.output1_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        self.select_output1_button = ctk.CTkButton(self.output_frame, text="Pfad für Teil 1 ändern", command=self.select_output1_pdf)
        self.select_output1_button.grid(row=1, column=0, padx=10, pady=(0, 5))

        # Label und Button für Output Teil 2
        self.output2_label = ctk.CTkLabel(self.output_frame, text="Output Teil 2: Standardpfad wird verwendet")
        self.output2_label.grid(row=2, column=0, padx=10, pady=(5, 5))

        self.select_output2_button = ctk.CTkButton(self.output_frame, text="Pfad für Teil 2 ändern", command=self.select_output2_pdf)
        self.select_output2_button.grid(row=3, column=0, padx=10, pady=(0, 10))

        # Button zum Starten des Split-Prozesses – rechts unten platziert
        self.split_button = ctk.CTkButton(self, text="PDF splitten", command=self.split_pdf)
        self.split_button.grid(row=5, column=0, padx=20, pady=(15, 20), sticky="e")

        # Split-Button initial deaktivieren, wird erst nach Dateiauswahl aktiviert
        self.split_button.configure(state="disabled")

    def select_input_pdf(self):
        """Öffnet einen Dateidialog zur Auswahl einer PDF-Datei, die gesplittet werden soll.
        Zeigt Dateiname und Seitenzahl an und setzt Standard-Ausgabepfade.
        """

        documents_dir = os.path.expanduser("~/Dokumente")  # Standardverzeichnis für Dokumente
        if not os.path.exists(documents_dir):
            documents_dir = os.path.expanduser("~/Documents")  # Fallback für englische Systeme

        filename = filedialog.askopenfilename(
            title="PDF zum Splitten auswählen",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=documents_dir
        )

        if filename:
            self.input_pdf = filename  # Pfad der ausgewählten PDF speichern
            self.file_label.configure(text=f"Ausgewählt: {os.path.basename(filename)}")  # Dateiname im Label anzeigen

            try:
                # Seitenzahl der ausgewählten PDF ermitteln
                page_count = self.pdf_utility.get_page_count(filename)
                self.page_info_label.configure(text=f"Gesamt: {page_count} Seiten")  # Seitenzahl anzeigen

                # Standard-Ausgabepfade für die beiden Teile setzen
                input_dir = os.path.dirname(filename)  # Verzeichnis der Eingabedatei
                base_name = os.path.splitext(os.path.basename(filename))[0]  # Dateiname ohne Endung
                self.output_part1 = os.path.join(input_dir, f"{base_name}_part1.pdf")  # Pfad für Teil 1
                self.output_part2 = os.path.join(input_dir, f"{base_name}_part2.pdf")  # Pfad für Teil 2
                self.output1_label.configure(text=f"Output Teil 1: {base_name}_part1.pdf")  # Label aktualisieren
                self.output2_label.configure(text=f"Output Teil 2: {base_name}_part2.pdf")  # Label aktualisieren

                self.split_button.configure(state="normal")  # Split-Button aktivieren

            except Exception as e:
                Messagebox("Fehler", f"Fehler beim Lesen der PDF: {str(e)}").messagebox_error()  # Fehlermeldung anzeigen
                Utils.write_to_log(f"Fehler beim Lesen der PDF: {str(e)}")  # Fehler ins Log schreiben
                self.reset_ui()  # UI zurücksetzen
        else:
            self.reset_ui()  # UI zurücksetzen, falls keine Datei ausgewählt wurde

    def select_output1_pdf(self):
        """Öffnet einen Dialog zur Auswahl des Speicherorts für den ersten Teil der gesplitteten PDF.
        Aktualisiert das zugehörige Label.
        """

        if not self.input_pdf:
            return  # Keine Eingabedatei ausgewählt, daher abbrechen

        initial_dir = os.path.dirname(self.input_pdf)  # Startverzeichnis für Dialog
        filename = filedialog.asksaveasfilename(
            title="Speicherort für Teil 1",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=initial_dir,
            defaultextension=".pdf"
        )

        if filename:
            self.output_part1 = filename  # Gewählten Pfad speichern
            self.output1_label.configure(text=f"Output Teil 1: {os.path.basename(filename)}")  # Label aktualisieren

    def select_output2_pdf(self):
        """Öffnet einen Dialog zur Auswahl des Speicherorts für den zweiten Teil der gesplitteten PDF.
        Aktualisiert das zugehörige Label.
        """

        if not self.input_pdf:
            return  # Keine Eingabedatei ausgewählt, daher abbrechen

        initial_dir = os.path.dirname(self.input_pdf)  # Startverzeichnis für Dialog
        filename = filedialog.asksaveasfilename(
            title="Speicherort für Teil 2",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=initial_dir,
            defaultextension=".pdf"
        )

        if filename:
            self.output_part2 = filename  # Gewählten Pfad speichern
            self.output2_label.configure(text=f"Output Teil 2: {os.path.basename(filename)}")  # Label aktualisieren

    def increase_value(self):
        """Erhöht den Wert im Seitenzahl-Eingabefeld um 1, solange das Maximum nicht überschritten wird.
        Prüft, ob eine PDF geladen ist und verhindert, dass der Wert über die maximale Seitenzahl hinausgeht.
        """

        try:
            current_value = int(self.page_entry.get())  # Aktuellen Wert holen
            if self.input_pdf:
                max_pages = self.pdf_utility.get_page_count(self.input_pdf) - 1  # Maximale Seite berechnen
                if current_value < max_pages:
                    self.page_entry.delete(0, "end")  # Feld leeren
                    self.page_entry.insert(0, str(current_value + 1))  # Wert um 1 erhöhen
        except ValueError:
            self.page_entry.delete(0, "end")  # Bei ungültiger Eingabe auf 1 setzen
            self.page_entry.insert(0, "1")

    def decrease_value(self):
        """Verringert den Wert im Seitenzahl-Eingabefeld um 1, mindestens jedoch auf 1.
        """

        try:
            current_value = int(self.page_entry.get())  # Aktuellen Wert holen
            if current_value > 1:
                self.page_entry.delete(0, "end")  # Feld leeren
                self.page_entry.insert(0, str(current_value - 1))  # Wert um 1 verringern
        except ValueError:
            self.page_entry.delete(0, "end")  # Bei ungültiger Eingabe auf 1
            self.page_entry.insert(0, "1")

    def validate_page_number(self, event=None):
        """Validiert die Eingabe im Seitenzahl-Eingabefeld.
        Stellt sicher, dass nur gültige Zahlen eingegeben werden und der Wert im erlaubten Bereich liegt.
        """

        try:
            value = self.page_entry.get()  # Aktuellen Wert aus dem Eingabefeld holen
            if value:
                page_num = int(value)  # Versuch, den Wert in eine Zahl umzuwandeln
                if self.input_pdf:
                    max_pages = self.pdf_utility.get_page_count(self.input_pdf) - 1  # Maximale erlaubte Seite berechnen
                    if page_num < 1:
                        self.page_entry.delete(0, "end")  # Wert zu klein: Feld leeren
                        self.page_entry.insert(0, "1")    # und auf 1 setzen
                    elif page_num > max_pages:
                        self.page_entry.delete(0, "end")      # Wert zu groß: Feld leeren
                        self.page_entry.insert(0, str(max_pages))  # und auf Maximum setzen
        except ValueError:
            # Ausnahme: Es wurde keine gültige Zahl eingegeben
            valid_chars = ''.join(c for c in self.page_entry.get() if c.isdigit())  # Nur Ziffern extrahieren
            if valid_chars:
                self.page_entry.delete(0, "end")     # Feld leeren
                self.page_entry.insert(0, valid_chars)  # Nur die gültigen Ziffern einfügen
            else:
                self.page_entry.delete(0, "end")     # Feld leeren
                self.page_entry.insert(0, "1")       # und auf 1 setzen

    def split_pdf(self):
        """Führt das Splitten der ausgewählten PDF-Datei durch.
        Validiert die Eingaben, führt den Split-Prozess durch und zeigt entsprechende Rückmeldungen an.
        """

        # Prüfen, ob eine Eingabedatei gesetzt ist
        if not self.input_pdf:
            Messagebox("PDF splitten", "Keine PDF-Datei zum Splitten ausgewählt.").messagebox_warning()  # Warnung anzeigen
            return

        # Prüfen, ob beide Ausgabepfade gesetzt sind
        if not self.output_part1 or not self.output_part2:
            Messagebox("Fehler", "Bitte wählen Sie Ausgabepfade für beide Teile aus.").messagebox_error()  # Fehler anzeigen
            return

        try:
            split_at = int(self.page_entry.get())  # Split-Seite aus dem Eingabefeld holen

            # Überprüfen, ob die Output-Verzeichnisse existieren, ggf. anlegen
            os.makedirs(os.path.dirname(self.output_part1), exist_ok=True)  # Ordner für Teil 1 anlegen
            os.makedirs(os.path.dirname(self.output_part2), exist_ok=True)  # Ordner für Teil 2 anlegen

            # PDF splitten und speichern
            PdfUtility.split_pdf(self.input_pdf, self.output_part1, self.output_part2, split_at)

            # Erfolgsmeldung an den Benutzer
            Messagebox(
                "PDF splitten",
                f"PDF wurde erfolgreich gesplittet und gespeichert unter:\n"
                f"Teil 1: {self.output_part1}\n"
                f"Teil 2: {self.output_part2}"
            ).messagebox_info()

        except Exception as e:
            # Fehlermeldung bei Problemen während des Split-Prozesses
            Messagebox("Fehler", f"Fehler beim Splitten der PDF:\n{str(e)}").messagebox_error()
            Utils.write_to_log(f"Fehler beim Splitten der PDF:\n{str(e)}")  # Fehler ins Log schreiben

    def reset_ui(self):
        """Setzt alle Labels, Eingabefelder und Variablen auf die Standardwerte zurück.
        """
        
        self.input_pdf = None  # Eingabepfad zurücksetzen
        self.output_part1 = None  # Ausgabepfad Teil 1 zurücksetzen
        self.output_part2 = None  # Ausgabepfad Teil 2 zurücksetzen
        self.file_label.configure(text="Keine Datei ausgewählt")  # Dateiname zurücksetzen
        self.page_info_label.configure(text="")  # Seiteninfo zurücksetzen
        self.output1_label.configure(text="Output Teil 1: Standardpfad wird verwendet")  # Label Teil 1 zurücksetzen
        self.output2_label.configure(text="Output Teil 2: Standardpfad wird verwendet")  # Label Teil 2 zurücksetzen
        self.page_entry.delete(0, "end")  # Eingabefeld leeren
        self.page_entry.insert(0, "1")  # Standardwert setzen
        self.split_button.configure(state="disabled")  # Split-Button deaktivieren