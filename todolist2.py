import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import json

class TodolistApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Todo List App")
        self.geometry("550x550")

        # Appliquer un style (thème par défaut)
        self.style = Style(theme="minty")  # 🌿 Thème initial
        self.configure(bg=self.style.colors.bg)  # Fond de la fenêtre selon le thème
        
        # Liste des thèmes disponibles
        self.theme_var = tk.StringVar(value="minty")
        themes = ["minty", "darkly", "flatly", "journal", "cyborg", "solar", "superhero"]

        # Sélecteur de thème
        theme_label = ttk.Label(self, text="Choisir un thème :", font=("Arial", 12))
        theme_label.pack(pady=5)

        theme_menu = ttk.Combobox(self, textvariable=self.theme_var, values=themes, state="readonly")
        theme_menu.pack(pady=5)
        theme_menu.bind("<<ComboboxSelected>>", self.change_theme)  # Changer le thème dynamiquement

        # Placeholder par défaut
        self.placeholders = ["Tâche...", "Date...", "Description...", "Priorité..."]
        
        # Cadre pour les entrées
        input_frame = tk.Frame(self, bg=self.style.colors.primary)
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Champs d'entrée avec placeholders
        self.entries = []
        for placeholder in self.placeholders:
            entry = ttk.Entry(input_frame, font=("Arial", 12), width=45, foreground="gray")
            entry.pack(pady=5, padx=10)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self.clear_placeholder(event, e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self.restore_placeholder(event, e, p))
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
    
    def change_theme(self, event):
        """ Change la couleur de l'interface en fonction du thème sélectionné """
        selected_theme = self.theme_var.get()
        self.style.theme_use(selected_theme)
        self.configure(bg=self.style.colors.bg)  # Adapter le fond de la fenêtre
        print(f"🎨 Thème changé : {selected_theme}")

    def clear_placeholder(self, event, entry, placeholder):
        """ Efface le texte placeholder lorsqu'on clique sur le champ. """
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.configure(foreground="black")
    
    def restore_placeholder(self, event, entry, placeholder):
        """ Remet le placeholder si le champ est vide. """
        if entry.get().strip() == "":
            entry.insert(0, placeholder)
            entry.configure(foreground="gray")
    
    def add_task(self):
        """ Ajoute une tâche avec les 4 informations dans le fichier JSON et l'affiche. """
        values = [entry.get().strip() for entry in self.entries]
        
        # Vérifier si tous les champs sont remplis
        if any(val == placeholder or val == "" for val, placeholder in zip(values, self.placeholders)):
            messagebox.showwarning("Entrée incomplète", "Veuillez remplir tous les champs.")
            return
        
        task_data = {"Tâche": values[0], "Date": values[1], "Description": values[2], "Priorité": values[3]}
        
        # Ajouter à la liste affichée
        self.task_list.insert(tk.END, f"{values[0]} - {values[1]} - {values[2]} - {values[3]}")
        
        # Sauvegarde dans JSON
        self.save_task_to_json(task_data)
        
        # Réinitialiser les champs
        for entry, placeholder in zip(self.entries, self.placeholders):
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
    
    def delete_task(self):
        """ Supprime la tâche sélectionnée. """
        try:
            task_index = self.task_list.curselection()[0]
            self.task_list.delete(task_index)
            self.save_all_tasks_to_json()
        except IndexError:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une tâche.")
    
    def view_stats(self):
        """ Affiche le nombre total de tâches. """
        total_count = self.task_list.size()
        messagebox.showinfo("Statistiques", f"Tâches totales: {total_count}")
    
    def save_task_to_json(self, task_data):
        """ Sauvegarde une nouvelle tâche dans le fichier JSON. """
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            tasks = []
        
        tasks.append(task_data)
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    
    def save_all_tasks_to_json(self):
        """ Sauvegarde toutes les tâches affichées dans le fichier JSON. """
        tasks = []
        for i in range(self.task_list.size()):
            values = self.task_list.get(i).split(" - ")
            if len(values) == 4:
                tasks.append({"Tâche": values[0], "Date": values[1], "Description": values[2], "Priorité": values[3]})
        
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    
    def load_tasks(self):
        """ Charge les tâches depuis le fichier JSON et les affiche. """
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                tasks = json.load(f)
                
            for task in tasks:
                if isinstance(task, dict) and all(k in task for k in ["Tâche", "Date", "Description", "Priorité"]):
                    self.task_list.insert(tk.END, f"{task['Tâche']} - {task['Date']} - {task['Description']} - {task['Priorité']}")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

if __name__ == '__main__':
    app = TodolistApp()
    app.mainloop()
