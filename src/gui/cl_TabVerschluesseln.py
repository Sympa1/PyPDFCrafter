import customtkinter as ctk
from tkinter import filedialog
import os
import re
from .cl_Messagebox import Messagebox
from classes import PdfUtility


class TabVerschluesseln(ctk.CTkFrame):
    """TabVerschluesseln ist ein Frame für die GUI, der es ermöglicht, PDF-Dateien zu verschlüsseln und zu entschlüsseln.
    """
    
    def __init__(self, master):
        super().__init__(master)
        self.selected_file = None

        # Spalte 0 und 1 je gleich gewichtet → jede belegt die Hälfte der Breite
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Button zum Auswählen einer PDF-Datei – über beide Spalten zentriert
        self.select_button = ctk.CTkButton(self, text="PDF auswählen", command=self.select_pdf, width=180)
        self.select_button.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5))

        # Label zur Anzeige des aktuell gewählten Dateipfads – über beide Spalten, zentriert
        self.file_label = ctk.CTkLabel(self, text="Keine Datei ausgewählt", anchor="center")
        self.file_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15))

        # Eingabefeld für das Passwort – Event-Binding löst Stärkeprüfung bei jedem Tastendruck aus
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Passwort", show="*", width=300)
        self.password_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 5))
        self.password_entry.bind("<KeyRelease>", self.update_password_strength)

        # Fortschrittsbalken zur visuellen Darstellung der Passwortstärke
        self.strength_bar = ctk.CTkProgressBar(self, width=300)
        self.strength_bar.set(0)  # Startwert: leer
        self.strength_bar.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 2))

        # Label zur Anzeige der Passwortstärke als Text
        self.strength_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.strength_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 5))

        # Checkliste der Passwortkriterien – jedes Label steht für ein Kriterium
        # Startzustand: alle Kriterien nicht erfüllt (✗, grau)
        criteria_texts = [
            "Mindestens 15 Zeichen",
            "Großbuchstabe (A-Z)",
            "Zahl (0-9)",
            "Sonderzeichen (!@#...)",
        ]

        # Frame als Container für die Checkliste
        self.criteria_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.criteria_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10))

        # Ein Label pro Kriterium erstellen und in einer Liste speichern
        # So können wir sie später per Index gezielt aktualisieren
        self.criteria_labels = []
        for text in criteria_texts:
            label = ctk.CTkLabel(self.criteria_frame, text=f"✗  {text}", text_color="gray")
            label.pack(anchor="w", pady=1)
            self.criteria_labels.append(label)

        # Checkbox zum Anzeigen/Verbergen des Passworts – über beide Spalten zentriert
        self.show_pw_var = ctk.BooleanVar()
        self.show_pw_checkbox = ctk.CTkCheckBox(self, text="Passwort anzeigen", variable=self.show_pw_var, command=self.toggle_password)
        self.show_pw_checkbox.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 20))

        # Button zum Verschlüsseln der PDF – über beide Spalten zentriert
        self.encrypt_button = ctk.CTkButton(self, text="PDF verschlüsseln", command=self.encrypt_pdf, width=180)
        self.encrypt_button.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 10))

        # Button zum Entschlüsseln der PDF – über beide Spalten zentriert
        self.decrypt_button = ctk.CTkButton(self, text="PDF entschlüsseln", command=self.decrypt_pdf, width=180)
        self.decrypt_button.grid(row=8, column=0, columnspan=2, padx=20, pady=(0, 20))

    @staticmethod
    def evaluate_password_strength(password: str) -> tuple[int, str, str, list[bool]]:
        """Bewertet die Stärke eines Passworts anhand mehrerer Kriterien.

        Kriterien (je 1 Punkt):
        - Mindestlänge von 8 Zeichen
        - Enthält Großbuchstaben (A-Z)
        - Enthält Zahlen (0-9)
        - Enthält Sonderzeichen (!@#$ ...)

        :param str password: Das zu bewertende Passwort.
        :return tuple: (score 0-4, Anzeigetext, Hex-Farbe, Liste der erfüllten Kriterien)
        """
        if not password:
            return 0, "", "gray", [False, False, False, False]

        # Jedes Kriterium einzeln prüfen und als Boolean speichern
        # Die Reihenfolge entspricht der Reihenfolge der Checklisten-Labels
        criteria = [
            len(password) >= 15,                      # Mindestlänge
            bool(re.search(r"[A-Z]", password)),      # [A-Z] = Großbuchstabe
            bool(re.search(r"[0-9]", password)),      # [0-9] = Ziffer
            bool(re.search(r"[^A-Za-z0-9]", password)),  # [^...] = Sonderzeichen (kein Buchstabe/Ziffer)
        ]

        # Score = Anzahl der erfüllten Kriterien
        score = sum(criteria)

        # Score auf Stärke-Stufe und Farbe mappen
        strength_map = {
            1: ("Schwach",     "#e74c3c"),  # Rot
            2: ("Mittel",      "#e67e22"),  # Orange
            3: ("Stark",       "#49ae74"),  # Grün
            4: ("Sehr stark",  "#27ae60"),  # Dunkelgrün
        }

        text, color = strength_map.get(score, ("Zu kurz", "#e74c3c"))
        return score, text, color, criteria

    def update_password_strength(self, event=None):
        """Wird bei jedem Tastendruck im Passwortfeld aufgerufen.
        Aktualisiert Fortschrittsbalken, Stärke-Label und die Kriterien-Checkliste.
        """
        password = self.password_entry.get()
        score, text, color, criteria = self.evaluate_password_strength(password)

        # Fortschrittsbalken: score/4 ergibt einen Wert zwischen 0.0 und 1.0
        self.strength_bar.set(score / 4)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(text=text, text_color=color)

        # Jedes Kriterien-Label anhand des Boolean-Werts aktualisieren
        # criteria[i] und criteria_labels[i] haben dieselbe Reihenfolge
        criteria_texts = [
            "Mindestens 15 Zeichen",
            "Großbuchstabe (A-Z)",
            "Zahl (0-9)",
            "Sonderzeichen (!@#...)",
        ]
        for i, met in enumerate(criteria):
            if met:
                # Kriterium erfüllt: grünes Häkchen
                self.criteria_labels[i].configure(text=f"✓  {criteria_texts[i]}", text_color="#27ae60")
            else:
                # Kriterium nicht erfüllt: graues X
                self.criteria_labels[i].configure(text=f"✗  {criteria_texts[i]}", text_color="gray")

    def select_pdf(self):
        """Öffnet einen Dateidialog zur Auswahl einer PDF-Datei."""

        documents_dir = os.path.expanduser("~/Dokumente")
        if not os.path.exists(documents_dir):
            documents_dir = os.path.expanduser("~/Documents")
        filename = filedialog.askopenfilename(
            title="PDF auswählen",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=documents_dir
        )
        # Zeigt den gewählten Dateipfad im Label an
        if filename:
            self.selected_file = filename
            self.file_label.configure(text=filename)
        else:
            self.selected_file = None
            self.file_label.configure(text="Keine Datei ausgewählt")

    def toggle_password(self):
        """Zeigt oder verbirgt das Passwort im Eingabefeld je nach Checkbox-Status"""

        if self.show_pw_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def encrypt_pdf(self):
        """Öffnet einen Speichern-Dialog zum Speichern der verschlüsselten PDF."""

        if not self.selected_file:
            Messagebox("Fehler", "Bitte zuerst eine PDF-Datei auswählen!").messagebox_warning()
            return
        password = self.password_entry.get()
        if not password:
            Messagebox("Fehler", "Bitte ein Passwort eingeben!").messagebox_warning()
            return
        documents_dir = os.path.expanduser("~/Dokumente")
        if not os.path.exists(documents_dir):
            documents_dir = os.path.expanduser("~/Documents")
        save_path = filedialog.asksaveasfilename(
            title="Verschlüsselte PDF speichern",
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=documents_dir
        )
        # Prüft, ob ein Speicherpfad ausgewählt wurde
        if not save_path:
            Messagebox("Fehler", "Bitte einen Speicherpfad auswählen!").messagebox_warning()
            return
        
        # Ruft die Verschlüsselungsmethode auf
        PdfUtility.encrypt_pdf(self.selected_file, save_path, password)

        # Zeigt eine Info-Messagebox nach dem Verschlüsseln
        if save_path:
            # Hier würdest du das Verschlüsseln implementieren
            Messagebox("PDF verschlüsseln", f"PDF würde verschlüsselt gespeichert unter:\n{save_path}").messagebox_info()

    def decrypt_pdf(self):
        """Öffnet einen Speichern-Dialog zum Speichern der entschlüsselten PDF."""

        if not self.selected_file:
            Messagebox("Fehler", "Bitte zuerst eine verschlüsselte PDF-Datei auswählen!").messagebox_warning()
            return
        password = self.password_entry.get()
        if not password:
            Messagebox("Fehler", "Bitte das Passwort zum Entschlüsseln eingeben!").messagebox_warning()
            return
        documents_dir = os.path.expanduser("~/Dokumente")
        if not os.path.exists(documents_dir):
            documents_dir = os.path.expanduser("~/Documents")
        save_path = filedialog.asksaveasfilename(
            title="Entschlüsselte PDF speichern",
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")],
            initialdir=documents_dir
        )
        if not save_path:
            Messagebox("Fehler", "Bitte einen Speicherpfad auswählen!").messagebox_warning()
            return

        try:
            PdfUtility.decrypt_pdf(self.selected_file, save_path, password)
            Messagebox("PDF entschlüsseln", f"PDF wurde entschlüsselt gespeichert unter:\n{save_path}").messagebox_info()
        except Exception as e:
            Messagebox("Fehler", f"Fehler beim Entschlüsseln der PDF:\n{str(e)}").messagebox_error()