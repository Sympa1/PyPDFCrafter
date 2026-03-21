import customtkinter as ctk
from tkinter import filedialog
import os
from classes.cl_PdfUtility import PdfUtility
from .cl_Messagebox import Messagebox
from classes.cl_Utils import Utils

# TODO: Ich brauche einen "reset" der PDF Liste nach einem merge
# TODO: Eine Progressbar für den Mergeprozess

class TabMergen(ctk.CTkFrame):
    """
    Tab-Klasse für das Zusammenführen (Mergen) von PDF-Dateien.
    Erbt von ctk.CTkFrame und stellt die GUI-Komponenten für die PDF-Merge-Funktionalität bereit.
    """

    def __init__(self, master):
        super().__init__(master)
        # Instanzvariablen initialisieren
        self.file_list = []  # Liste der ausgewählten PDF-Dateien
        self.output_path = None  # Pfad für die Ausgabedatei
        self.pdf_utility = PdfUtility()  # Utility-Objekt für PDF-Operationen

        # Spalte 0 dehnt sich mit der Fensterbreite aus
        self.grid_columnconfigure(0, weight=1)
        # Zeile 2 (Textbox) dehnt sich mit der Fensterhöhe aus
        self.grid_rowconfigure(2, weight=1)

        # === GUI-ELEMENTE ERSTELLEN ===

        # Button zum Hinzufügen von PDF-Dateien – zentriert in der Zeile
        self.add_button = ctk.CTkButton(self, text="PDF hinzufügen", command=self.add_file)
        self.add_button.grid(row=0, column=0, padx=20, pady=(20, 0))

        # Label zur Anzeige der Anzahl ausgewählter PDF-Dateien
        self.file_label = ctk.CTkLabel(self, text="Keine Dateien ausgewählt")
        self.file_label.grid(row=1, column=0, padx=20, pady=(5, 0))

        # Textbox dehnt sich in alle Richtungen mit dem Fenster aus (sticky="nsew")
        self.listbox = ctk.CTkTextbox(self)
        self.listbox.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="nsew")
        self.listbox.configure(state="disabled")  # Readonly-Modus

        # Frame-Container für Output-Konfiguration – dehnt sich horizontal aus
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        # Label zur Anzeige des aktuellen Ausgabepfads
        self.output_label = ctk.CTkLabel(self.output_frame, text="Output: Standardpfad wird verwendet")
        self.output_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Button zur Änderung des Ausgabepfads – zentriert im Frame
        self.select_output_button = ctk.CTkButton(self.output_frame, text="Ausgabepfad ändern",
                                                  command=self.select_output_path)
        self.select_output_button.grid(row=1, column=0, padx=10, pady=(0, 10))

        # Hauptaktions-Button rechts unten platziert
        self.merge_button = ctk.CTkButton(self, text="PDFs zusammenführen", command=self.merge_pdfs)
        self.merge_button.grid(row=4, column=0, padx=20, pady=(15, 20), sticky="e")

        # Button initial deaktivieren (wird erst bei Dateiauswahl aktiviert)
        self.merge_button.configure(state="disabled")

    def add_file(self):
        """Öffnet einen Dateidialog zur Auswahl von PDF-Dateien und fügt sie zur Merge-Liste hinzu.
        Verhindert das Hinzufügen von Duplikaten und aktualisiert die GUI entsprechend.
        """

        # Standardverzeichnis ermitteln (Dokumente-Ordner)
        # unterstützt deutsche und englische Systemlokalisierung
        documents_dir = os.path.expanduser("~/Dokumente")
        if not os.path.exists(documents_dir):
            documents_dir = os.path.expanduser("~/Documents")  # Fallback für englische Systeme

        # Dateidialog zur Mehrfachauswahl von PDF-Dateien öffnen
        filenames = filedialog.askopenfilenames(
            title="PDF auswählen",
            filetypes=[("PDF-Dateien", "*.pdf")],  # Nur PDF-Dateien anzeigen
            initialdir=documents_dir
        )

        # Neue Dateien zur Liste hinzufügen (Duplikate werden übersprungen)
        for file in filenames:
            if file not in self.file_list:
                self.file_list.append(file)

        # GUI-Elemente aktualisieren
        self.update_listbox()

        # Button-Status und Label entsprechend der Dateiliste anpassen
        if self.file_list:
            self.merge_button.configure(state="normal")  # Button aktivieren
            self.file_label.configure(text=f"{len(self.file_list)} Datei(en) ausgewählt")
        else:
            self.merge_button.configure(state="disabled")  # Button deaktivieren
            self.file_label.configure(text="Keine Dateien ausgewählt")

    def select_output_path(self):
        """Öffnet einen Dialog zur Auswahl des Ausgabepfads für die zusammengeführte PDF-Datei.
        Aktualisiert das Output-Label mit dem gewählten Dateinamen.
        """

        # Standardverzeichnis ermitteln
        documents_dir = os.path.expanduser("~/Dokumente")
        if not os.path.exists(documents_dir):
            documents_dir = os.path.expanduser("~/Documents")

        # "Speichern unter"-Dialog öffnen
        save_path = filedialog.asksaveasfilename(
            title="Ziel-PDF speichern",
            defaultextension=".pdf",  # Automatische .pdf-Erweiterung
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=documents_dir
        )

        # Pfad speichern und GUI aktualisieren, falls ein Pfad gewählt wurde
        if save_path:
            self.output_path = save_path
            filename = os.path.basename(save_path)  # Nur Dateinamen ohne Pfad anzeigen
            self.output_label.configure(text=f"Output: {filename}")

    def update_listbox(self):
        """Aktualisiert die Textbox mit allen aktuell ausgewählten PDF-Dateipfaden.
        Zeigt jeden Dateipfad in einer separaten Zeile an.
        """

        # Textbox temporär bearbeitbar machen
        self.listbox.configure(state="normal")

        # Aktuellen Inhalt löschen
        self.listbox.delete("1.0", "end")

        # Alle Dateipfade in die Textbox einfügen
        for file in self.file_list:
            self.listbox.insert("end", file + "\n")

        # Textbox wieder aufreadonly setzen
        self.listbox.configure(state="disabled")

    def merge_pdfs(self):
        """Führt die ausgewählten PDF-Dateien zusammen.
        Validiert die Eingaben, führt den Merge-Prozess durch und zeigt entsprechende Rückmeldungen an.
        """
        
        # Sicherheitsabfrage: Falls keine Dateien ausgewählt wurden, Abbruch und Hinweis anzeigen
        if not self.file_list:
            Messagebox("PDF zusammenführen", "Keine PDF-Dateien zum Zusammenführen ausgewählt.").messagebox_warning()
            return

        # Standard-Ausgabepfad, falls keiner gewählt wurde
        if not self.output_path:
            documents_dir = os.path.expanduser("~/Dokumente")
            if not os.path.exists(documents_dir):
                documents_dir = os.path.expanduser("~/Documents")
            save_path = os.path.join(documents_dir, "zusammengefuehrt.pdf")
            self.output_path = save_path
            self.output_label.configure(text="Output: zusammengefuehrt.pdf")
        else:
            save_path = self.output_path

        # Merge-Prozess nur ausführen, wenn ein gültiger Speicherpfad vorhanden ist
        if save_path:
            try:
                # PDF-Merge-Operation durchführen
                PdfUtility.merge_pdf(self.file_list, save_path)

                # Erfolgsmeldung an den Benutzer
                Messagebox("PDF zusammenführen",
                           f"PDFs wurden erfolgreich zusammengeführt und gespeichert unter:\n{save_path}").messagebox_info()

            except Exception as e:
                # Fehlermeldung bei Problemen während des Merge-Prozesses
                error_message = f"Fehler beim Zusammenführen der PDFs:\n{str(e)}"
                Messagebox("Fehler", error_message).messagebox_error()
                Utils.write_to_log(error_message)