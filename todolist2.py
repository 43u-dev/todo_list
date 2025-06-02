import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class TodolistApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Todo List App")
        self.geometry("600x600")
        self.configure(bg="#f0f0f0")

        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        self.style.configure("TEntry", font=("Arial", 12), padding=5)

        self.placeholders = ["Tâche...", "Date...", "Description...", "Priorité..."]

        input_frame = tk.Frame(self, bg="#d1e7dd")
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        self.entries = []
        for placeholder in self.placeholders:
            entry = ttk.Entry(input_frame, font=("Arial", 12), width=45, foreground="gray")
            entry.pack(pady=5, padx=10)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self.clear_placeholder(event, e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self.restore_placeholder(event, e, p))
            self.entries.append(entry)

        ttk.Button(self, text="Ajouter", command=self.add_task).pack(pady=5)

        filter_frame = tk.Frame(self, bg="#f0f0f0")
        filter_frame.pack(pady=5)
        tk.Label(filter_frame, text="Filtrer par priorité:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.priority_filter = ttk.Combobox(filter_frame, values=["", "Basse", "Moyenne", "Haute"], width=15)
        self.priority_filter.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Filtrer", command=self.filter_tasks).pack(side=tk.LEFT, padx=5)
        tk.Label(filter_frame, text="Rechercher:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(filter_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Chercher", command=self.search_tasks).pack(side=tk.LEFT)

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

        ttk.Button(self, text="Supprimer", command=self.delete_task).pack(pady=5)
        ttk.Button(self, text="Marquer comme terminée", command=self.mark_done).pack(pady=5)
        ttk.Button(self, text="Voir Statistiques", command=self.view_stats).pack(pady=10)

        self.load_tasks()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS taskes3 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                date TEXT,
                description TEXT,
                priority TEXT,
                done INTEGER DEFAULT 0
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

    def mark_done(self):
        try:
            task_index = self.task_list.curselection()[0]
            task_text = self.task_list.get(task_index)
            task_name = task_text.split(" - ")[0]

            self.cursor.execute("UPDATE taskes3 SET done = 1 WHERE task = ?", (task_name,))
            self.conn.commit()

            self.task_list.itemconfig(task_index, fg="gray")
        except IndexError:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une tâche.")

    def view_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM taskes3")
        total = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM taskes3 WHERE done = 1")
        done = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM taskes3 WHERE done = 0")
        not_done = self.cursor.fetchone()[0]

        messagebox.showinfo("Statistiques", f"Tâches totales: {total}\nTerminées: {done}\nNon terminées: {not_done}")

    def load_tasks(self):
        self.task_list.delete(0, tk.END)
        self.cursor.execute("SELECT task, date, description, priority, done FROM taskes3")
        for idx, task in enumerate(self.cursor.fetchall()):
            display = " - ".join(task[:-1])
            self.task_list.insert(tk.END, display)
            if task[-1] == 1:
                self.task_list.itemconfig(idx, fg="gray")

    def filter_tasks(self):
        priority = self.priority_filter.get()
        self.task_list.delete(0, tk.END)
        if priority:
            self.cursor.execute("SELECT task, date, description, priority FROM taskes3 WHERE priority = ?", (priority,))
        else:
            self.cursor.execute("SELECT task, date, description, priority FROM taskes3")

        for task in self.cursor.fetchall():
            self.task_list.insert(tk.END, " - ".join(task))

    def search_tasks(self):
        keyword = self.search_entry.get().strip().lower()
        self.task_list.delete(0, tk.END)
        self.cursor.execute("SELECT task, date, description, priority FROM taskes3")

        for task in self.cursor.fetchall():
            if any(keyword in str(field).lower() for field in task):
                self.task_list.insert(tk.END, " - ".join(task))

    def __del__(self):
        self.conn.close()

if __name__ == '__main__':
    app = TodolistApp()
    app.mainloop()
