import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class TodolistApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Todo List App")
        self.geometry("550x550")
        self.configure(bg="#f0f0f0")  # Fond de la fenêtre

        # Connexion à la base de données SQLite
        self.conn = sqlite3.connect("taskes3.db")
        self.cursor = self.conn.cursor()
        self.create_table()  # Création de la table si elle n'existe pas

        # Style personnalisé pour les widgets ttk
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        self.style.configure("TEntry", font=("Arial", 12), padding=5)

        # Placeholder par défaut
        self.placeholders = ["Tâche...", "Date...", "Description...", "Priorité..."]

        # Cadre pour les entrées
        input_frame = tk.Frame(self, bg="#d1e7dd")
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        # Champs d'entrée
        self.entries = []
        for placeholder in self.placeholders:
            entry = ttk.Entry(input_frame, font=("Arial", 12), width=45, foreground="gray")
            entry.pack(pady=5, padx=10)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self.clear_placeholder(event, e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self.restore_placeholder(event, e, p))
            self.entries.append(entry)

        # Bouton Ajouter
        ttk.Button(self, text="Ajouter", command=self.add_task).pack(pady=5)

        # Zone d'affichage des tâches
        list_frame = tk.Frame(self, bg="#ffffff")
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.task_list = tk.Listbox(
            list_frame, font=("Arial", 14), height=10, selectmode=tk.SINGLE,
            bg="#ffffff", fg="black", highlightbackground="#87CEEB", highlightthickness=2
        )
        self.task_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_list.config(yscrollcommand=scrollbar.set)

        # Boutons de gestion
        ttk.Button(self, text="Supprimer", command=self.delete_task).pack(pady=5)
        ttk.Button(self, text="Voir Statistiques", command=self.view_stats).pack(pady=10)

        # Charger les tâches existantes
        self.load_tasks()

    def create_table(self):
        """Crée la table des tâches si elle n'existe pas"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS taskes3(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                date TEXT,
                description TEXT,
                priority TEXT
            )
        ''')
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
            messagebox.showwarning("Entrée incomplète", "Veuillez remplir tous les champs.")
            return
        
        self.cursor.execute("INSERT INTO taskes3 (task, date, description, priority) VALUES (?, ?, ?, ?)", values)
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
            
            self.cursor.execute("DELETE FROM taskes3 WHERE task = ?", (task_name,))
            self.conn.commit()
            
            self.task_list.delete(task_index)
        except IndexError:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une tâche.")

    def view_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM taskes3")
        total_count = self.cursor.fetchone()[0]
        messagebox.showinfo("Statistiques", f"Tâches totales: {total_count}")

    def load_tasks(self):
        self.cursor.execute("SELECT task, date, description, priority FROM taskes3")
        taskes3 = self.cursor.fetchall()
        for task in taskes3:
            self.task_list.insert(tk.END, " - ".join(task))

    def __del__(self):
        """Ferme la connexion à la base de données à la fermeture de l'application."""
        self.conn.close()

if __name__ == '__main__':
    app = TodolistApp()
    app.mainloop()
