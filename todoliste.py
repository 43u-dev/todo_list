import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class TodolistApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Todo List App")
        self.geometry("500x300")
        self.configure(bg="#f0f0f0")

        # Connexion à la base de données SQLite
        self.conn = sqlite3.connect("tache1.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        # Style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))

        # Champs de saisie
        self.placeholders = ["Tâche...", "Date...", "Description...", "Priorité..."]
        self.entries = []

        input_frame = tk.Frame(self, bg="#d1e7dd")
        input_frame.pack(pady=20, padx=10)

        for placeholder in self.placeholders:
            entry = ttk.Entry(input_frame, font=("Arial", 12), width=40, foreground="gray")
            entry.pack(pady=5)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self.clear_placeholder(event, e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self.restore_placeholder(event, e, p))
            self.entries.append(entry)

        # Bouton pour ajouter
        ttk.Button(self, text="Ajouter dans la base", command=self.add_task).pack(pady=10)

    def create_table(self):
        """Créer la table dans la base de données si elle n'existe pas."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tache1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                date TEXT,
                description TEXT,
                priority TEXT
            )
        """)
        self.conn.commit()

    def clear_placeholder(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.configure(foreground="black")

    def restore_placeholder(self, event, entry, placeholder):
        if entry.get().strip() == "":
            entry.insert(0, placeholder)
            entry.configure(foreground="gray")

    def add_task(self):
        values = [entry.get().strip() for entry in self.entries]
        if any(val == placeholder or val == "" for val, placeholder in zip(values, self.placeholders)):
            messagebox.showwarning("Champs incomplets", "Veuillez remplir tous les champs.")
            return

        self.cursor.execute(
            "INSERT INTO tasks (task, date, description, priority) VALUES (?, ?, ?, ?)",
            values
        )
        self.conn.commit()

        messagebox.showinfo("Succès", "Tâche enregistrée dans la base SQLite.")
        
        # Réinitialiser les champs
        for entry, placeholder in zip(self.entries, self.placeholders):
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.configure(foreground="gray")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    app = TodolistApp()
    app.mainloop()
