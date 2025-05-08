import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import sqlite3
from functools import partiapipl  # Ajout de functools.partial

class TodolistApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Todo List App")
        self.geometry("550x550")

        # Connexion à la base de données SQLite
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.create_table()  # Création de la table si elle n'existe pas

        # Appliquer un style (thème par défaut)
        self.style = Style(theme="minty")
        self.configure(bg=self.style.colors.bg)
        
        # Liste des thèmes disponibles
        self.theme_var = tk.StringVar(value="minty")
        themes = ["minty", "darkly", "flatly", "journal", "cyborg", "solar", "superhero"]

        # Sélecteur de thème
        ttk.Label(self, text="Choisir un thème :", font=("Arial", 12)).pack(pady=5)
        theme_menu = ttk.Combobox(self, textvariable=self.theme_var, values=themes, state="readonly")
        theme_menu.pack(pady=5)
        theme_menu.bind("<<ComboboxSelected>>", self.change_theme)

        # Placeholder par défaut
        self.placeholders = ["Tâche...", "Date...", "Description...", "Priorité..."]

        # Cadre pour les entrées
        input_frame = tk.Frame(self, bg=self.style.colors.primary)
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        # Champs d'entrée
        self.entries = []
        for placeholder in self.placeholders:
            entry = ttk.Entry(input_frame, font=("Arial", 12), width=45, foreground="gray")
            entry.pack(pady=5, padx=10)
            entry.insert(0, placeholder)

            # Utilisation de partial pour éviter l'erreur de capture de variable
            entry.bind("<FocusIn>", partial(self.clear_placeholder, entry=entry, placeholder=placeholder))
            entry.bind("<FocusOut>", partial(self.restore_placeholder, entry=entry, placeholder=placeholder))

            self.entries.append(entry)

        # Bouton Ajouter
        ttk.Button(self, text="Ajouter", command=self.add_task, bootstyle="success").pack(pady=5)

        # Zone d'affichage des tâches
        list_frame = tk.Frame(self, bg=self.style.colors.light)
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.task_list = tk.Listbox(
            list_frame, font=("Arial", 14), height=10, selectmode=tk.SINGLE,
            bg=self.style.colors.light, fg="black", highlightbackground=self.style.colors.info, highlightthickness=2
        )
        self.task_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_list.config(yscrollcommand=scrollbar.set)

        # Boutons de gestion
        ttk.Button(self, text="Supprimer", command=self.delete_task, bootstyle="danger").pack(pady=5)
        ttk.Button(self, text="Voir Statistiques", command=self.view_stats, bootstyle="info").pack(pady=10)

        # Charger les tâches existantes
        self.load_tasks()

    def create_table(self):
        """Crée la table des tâches si elle n'existe pas"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                date TEXT,
                description TEXT,
                priority TEXT
            )
        ''')
        self.conn.commit()

    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.style.theme_use(selected_theme)
        self.configure(bg=self.style.colors.bg)

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
            messagebox.showwarning("Entrée incomplète", "Veuillez remplir tous les champs.")
            return
        
        self.cursor.execute("INSERT INTO tasks (task, date, description, priority) VALUES (?, ?, ?, ?)", values)
        self.conn.commit()
        self.task_list.insert(tk.END, " - ".join(values))
        
        for entry, placeholder in zip(self.entries, self.placeholders):
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)

    def delete_task(self):
        try:
            task_index = self.task_list.curselection()[0]
            task_text = self.task_list.get(task_index)
            task_name = task_text.split(" - ")[0]
            
            self.cursor.execute("DELETE FROM tasks WHERE task = ?", (task_name,))
            self.conn.commit()
            
            self.task_list.delete(task_index)
        except IndexError:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une tâche.")

    def view_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        total_count = self.cursor.fetchone()[0]
        messagebox.showinfo("Statistiques", f"Tâches totales: {total_count}")

    def load_tasks(self):
        self.cursor.execute("SELECT task, date, description, priority FROM tasks")
        tasks = self.cursor.fetchall()
        for task in tasks:
            self.task_list.insert(tk.END, " - ".join(task))

    def __del__(self):
        """Ferme la connexion à la base de données à la fermeture de l'application."""
        self.conn.close()

if __name__ == '__main__':
    app = TodolistApp()
    app.mainloop()
