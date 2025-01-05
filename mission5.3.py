# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 20:32:40 2025

@author: laura
"""

import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")

def get_next_id(collection_name, id_field, nom_bdd):
    db = client[nom_bdd]
    collection = db[collection_name]
    
    # Trouver le plus grand ID
    result = collection.find_one(sort=[(id_field, -1)])
    if result and id_field in result:
        return result[id_field] + 1
    return 1  # Si la collection est vide, commencer à 1

def is_id_unique(collection_name, id_field, id_value, nom_bdd):
    db = client[nom_bdd]
    collection = db[collection_name]
    return collection.find_one({id_field: id_value}) is None

# Fonction pour insérer les données dans MongoDB
def insert_into_mongodb(collection_name, data, nom_bdd):
    try:
        db = client[nom_bdd]
        collection = db[collection_name]
        collection.insert_one(data)
        messagebox.showinfo("Succès", f"Données insérées avec succès dans la collection {collection_name}.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'insérer les données : {e}")
        
        
# Fonction pour sauvegarder les données dans un fichier JSON avec un nom choisi par l'utilisateur
def save_to_json(file_name, data):
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Succès", f"Données enregistrées dans le fichier {file_name}.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'enregistrer les données dans le fichier : {e}")
        
        
def modele_film():
    def sauvegarde_film():
        film_id = film_id_var.get()

        # Vérifier si l'ID est unique dans la collection "film"
        if not is_id_unique("film", "film_id", film_id, "ds_pagila"):
            messagebox.showerror("Erreur", "Cet ID de film existe déjà dans la base de données.")
            return

        # Récupérer les données du film
        data = {
            "film_id": film_id,
            "title": title_var.get(),
            "description": description_var.get(),
            "language_id": language_id_var.get(),
            "original_language_id": original_language_id_var.get(),
            "actors": actors_list  # Liste des acteurs associés au film
        }

        # Sauvegarder dans le fichier JSON choisi
        nom_fichier_json = file_name_var.get()
        if nom_fichier_json:
            save_to_json(nom_fichier_json, data)
            insert_into_mongodb("film", data, "ds_pagila")
            window.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de fichier pour enregistrer.")

    def ajoute_acteur_film():
        actor_id = actor_id_var.get()

        # Vérifier si l'ID de l'acteur est unique dans la collection "actors"
        if not is_id_unique("acteur", "actor_id", actor_id, "ds_pagila"):
            messagebox.showerror("Erreur", "Cet ID d'acteur existe déjà dans la base de données.")
            return

        actor_first_name = actor_first_name_var.get()
        actor_last_name = actor_last_name_var.get()

        if actor_first_name and actor_last_name:
            actors_list.append({
                "actor_id": actor_id,
                "first_name": actor_first_name,
                "last_name": actor_last_name
            })
            actor_listbox.insert(tk.END, f"{actor_first_name} {actor_last_name} (ID: {actor_id})")
            actor_id_var.set("")  # Réinitialiser les champs
            actor_first_name_var.set("")
            actor_last_name_var.set("")
        else:
            messagebox.showerror("Erreur", "Veuillez entrer le prénom et le nom de l'acteur.")

    window = tk.Toplevel()
    window.title("Modèle Film avec Acteurs")

    # Obtenir le prochain ID automatiquement
    next_film_id = get_next_id("film", "film_id", "ds_pagila")

    # Variables pour le film
    film_id_var = tk.IntVar(value=next_film_id)  # Pré-remplir avec l'ID généré automatiquement
    title_var = tk.StringVar()
    description_var = tk.StringVar()
    language_id_var = tk.IntVar()
    original_language_id_var = tk.IntVar()
    file_name_var = tk.StringVar()  # Variable pour le nom du fichier JSON

    # Labels pour le film
    tk.Label(window, text="ID du Film:").grid(row=0, column=0)
    tk.Label(window, text="Titre:").grid(row=1, column=0)
    tk.Label(window, text="Description:").grid(row=2, column=0)
    tk.Label(window, text="ID de la Langue:").grid(row=3, column=0)
    tk.Label(window, text="ID de la Langue Originale:").grid(row=4, column=0)
    tk.Label(window, text="Nom du fichier JSON:").grid(row=5, column=0)

    # Entrées pour le film
    tk.Entry(window, textvariable=film_id_var).grid(row=0, column=1)  # Pré-rempli mais modifiable
    tk.Entry(window, textvariable=title_var).grid(row=1, column=1)
    tk.Entry(window, textvariable=description_var).grid(row=2, column=1)
    tk.Entry(window, textvariable=language_id_var).grid(row=3, column=1)
    tk.Entry(window, textvariable=original_language_id_var).grid(row=4, column=1)
    tk.Entry(window, textvariable=file_name_var).grid(row=5, column=1)

    # Section pour ajouter des acteurs
    tk.Label(window, text="ID de l'Acteur:").grid(row=6, column=0)
    tk.Label(window, text="Prénom de l'Acteur:").grid(row=7, column=0)
    tk.Label(window, text="Nom de l'Acteur:").grid(row=8, column=0)

    actor_id_var = tk.IntVar()
    actor_first_name_var = tk.StringVar()
    actor_last_name_var = tk.StringVar()

    tk.Entry(window, textvariable=actor_id_var).grid(row=6, column=1)
    tk.Entry(window, textvariable=actor_first_name_var).grid(row=7, column=1)
    tk.Entry(window, textvariable=actor_last_name_var).grid(row=8, column=1)

    tk.Button(window, text="Ajouter un acteur", command=ajoute_acteur_film).grid(row=9, column=0, columnspan=2)

    # Liste des acteurs ajoutés au film
    actor_listbox = tk.Listbox(window, height=4, width=50)
    actor_listbox.grid(row=10, column=0, columnspan=2)

    actors_list = []  # Liste pour stocker les acteurs associés au film

    # Bouton pour sauvegarder le film
    tk.Button(window, text="Sauvegarder le Film", command=sauvegarde_film).grid(row=11, column=0, columnspan=2)

    
# Interface graphique pour le modèle acteur avec films
def modele_acteur():
    def sauvegarde_acteur():
        acteur_id = actor_id_var.get()
        
        # Vérifier si l'ID est unique dans la collection "acteur"
        if not is_id_unique("acteur", "actor_id", acteur_id, "ds_pagila"):
            messagebox.showerror("Erreur", "Cet ID d'acteur existe déjà dans la base de données.")
            return
        
        # Récupérer les données de l'acteur
        data = {
            "actor_id": actor_id_var.get(),
            "first_name": first_name_var.get(),
            "last_name": last_name_var.get(),
            "films": films_list  # Liste des films associés à l'acteur
        }

        # Sauvegarder dans le fichier JSON choisi
        nom_fichier_json = file_name_var.get()
        if nom_fichier_json:
            save_to_json(nom_fichier_json, data)
            insert_into_mongodb("acteur", data, "ds_pagila")
            window.destroy()
        else:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de fichier pour enregistrer.")

    def ajoute_film_acteur():
        film_id = film_id_var.get()
        film_title = film_title_var.get()
        film_description = film_description_var.get()
        language_id = language_id_var.get()
        original_language_id = original_language_id_var.get()
        if film_id and film_title and film_description and language_id and original_language_id:
            films_list.append({
                "film_id": film_id,
                "title": film_title,
                "description": film_description,
                "language_id": language_id,
                "original_language_id": original_language_id
            })
            film_listbox.insert(tk.END, f"{film_title} (ID: {film_id})")
            film_id_var.set("")
            film_title_var.set("")
            film_description_var.set("")
            language_id_var.set("")
            original_language_id_var.set("")
        else:
            messagebox.showerror("Erreur", "Veuillez entrer tous les détails du film.")

    window = tk.Toplevel()
    window.title("Modèle Acteur avec Films")

    # Obtenir le prochain ID automatiquement
    next_actor_id = get_next_id("acteur", "film_id", "ds_pagila")
    
    
    # Labels pour l'acteur
    tk.Label(window, text="ID de l'Acteur:").grid(row=0, column=0)
    tk.Label(window, text="Prénom de l'Acteur:").grid(row=1, column=0)
    tk.Label(window, text="Nom de l'Acteur:").grid(row=2, column=0)
    tk.Label(window, text="Nom du fichier JSON:").grid(row=3, column=0)

    # Variables pour l'acteur
    actor_id_var = tk.IntVar(value=next_actor_id)
    first_name_var = tk.StringVar()
    last_name_var = tk.StringVar()
    file_name_var = tk.StringVar()

    # Entrées pour l'acteur
    tk.Entry(window, textvariable=actor_id_var).grid(row=0, column=1)
    tk.Entry(window, textvariable=first_name_var).grid(row=1, column=1)
    tk.Entry(window, textvariable=last_name_var).grid(row=2, column=1)
    tk.Entry(window, textvariable=file_name_var).grid(row=3, column=1)

    # Section pour ajouter des films
    tk.Label(window, text="ID du Film:").grid(row=4, column=0)
    tk.Label(window, text="Titre du Film:").grid(row=5, column=0)
    tk.Label(window, text="Description:").grid(row=6, column=0)
    tk.Label(window, text="ID de la Langue:").grid(row=7, column=0)
    tk.Label(window, text="ID de la Langue Originale:").grid(row=8, column=0)

    film_id_var = tk.IntVar()
    film_title_var = tk.StringVar()
    film_description_var = tk.StringVar()
    language_id_var = tk.IntVar()
    original_language_id_var = tk.IntVar()

    tk.Entry(window, textvariable=film_id_var).grid(row=4, column=1)
    tk.Entry(window, textvariable=film_title_var).grid(row=5, column=1)
    tk.Entry(window, textvariable=film_description_var).grid(row=6, column=1)
    tk.Entry(window, textvariable=language_id_var).grid(row=7, column=1)
    tk.Entry(window, textvariable=original_language_id_var).grid(row=8, column=1)

    tk.Button(window, text="Ajouter un film", command=ajoute_film_acteur).grid(row=9, column=0, columnspan=2)

    # Liste des films ajoutés à l'acteur
    film_listbox = tk.Listbox(window, height=4, width=50)
    film_listbox.grid(row=10, column=0, columnspan=2)

    films_list = []  # Liste pour stocker les films associés à l'acteur

    # Bouton pour sauvegarder l'acteur
    tk.Button(window, text="Sauvegarder l'Acteur", command=sauvegarde_acteur).grid(row=11, column=0, columnspan=2)

# Fenêtre principale
root = tk.Tk()
root.title("Saisie de Documents")
root.geometry("400x300")

tk.Label(root, text="Choisissez un modèle:").pack(pady=10)
tk.Button(root, text="Modèle Film avec Acteurs", command=modele_film).pack(pady=5)
tk.Button(root, text="Modèle Acteur avec Films", command=modele_acteur).pack(pady=5)

root.mainloop()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        