import psycopg2
import pandas as pd

# %%=============================================================================
# Création des bases de données 
# =============================================================================

# connexion à postgres
conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="******",
                        port="5432")

conn.autocommit = True
cur = conn.cursor()

# nombre de tables à insérer
nb_table = 5


# création de chaque base de données
for n in range(nb_table): 
    try:
        requete = "CREATE DATABASE ds_pagila"+str(n+1)+";"
        cur.execute(requete)
        print("Base de données créée avec succès.")
    except psycopg2.Error as e:
        print("Erreur lors de la création de la base de données ds_pagila",str(n+1),":", e)
cur.close()
conn.close()



#%% =============================================================================
# Création des tables dans les bases de données 
# =============================================================================

# script sql de la strcuture des tables 
with open('pagilaSAE-schema.sql', 'r') as fichier:
    script_sql = fichier.read()

# script exécuté pour chaque table
for n in range(nb_table): 
    nom_bdd= "ds_pagila"+str(n+1)
    conn = psycopg2.connect(database=nom_bdd,
                        host="localhost",
                        user="postgres",
                        password="ldeloffr",
                        port="5432")
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        cur.execute(script_sql)
        print("Tables créées avec succès.")
    except psycopg2.Error as e:
        print("Erreur lors de la création des tables:", e)
    cur.close()
    conn.close()



# %%=============================================================================
# Importation des données du csv 
# =============================================================================

for n in range (nb_table) :
    # lecture de chaque csv et de leurs numéros pour les mettre dans la table correspondante
    csv_actor = pd.read_csv("csv/actor"+str(n+1)+".csv", delimiter = ",")
    csv_film_actor = pd.read_csv("csv/film_actor"+str(n+1)+".csv", delimiter = ",")
    csv_film = pd.read_csv("csv/film"+str(n+1)+".csv", delimiter = ",")
    
    
    nom_bdd= "ds_pagila"+str(n+1)
    conn = psycopg2.connect(database=nom_bdd,
                        host="localhost",
                        user="postgres",
                        password="ldeloffr",
                        port="5432")
    conn.autocommit = True
    cur = conn.cursor()
    

    # insertion des valeurs acteurs
    for index, row in csv_actor.iterrows():
        try:
            cur.execute("""INSERT INTO actor (actor_id, first_name, last_name)
                VALUES (%s, %s, %s) """, (int(row['actor_id']), row['first_name'], row['last_name']))
            print("Valeurs insérées avec succès.")
        except psycopg2.Error as e:
            print("Erreur lors de l'insertion des valeurs:", e)

    # insertion des valeurs film
    for index, row in csv_film.iterrows():
        try:
            film_id = int(row['film_id'])
            language_id = int(row['language_id'])
            original_language_id = row['original_language_id'] if pd.notnull(row['original_language_id']) else None
    
            cur.execute("""INSERT INTO film (film_id, title, description, language_id, original_language_id)
                VALUES (%s, %s, %s, %s, %s)""", (film_id, row['title'], row['description'], 
                language_id, original_language_id))
            print("Valeurs insérées avec succès.")
        except psycopg2.Error as e:
            print("Erreur lors de l'insertion des valeurs:", e)
    
    # insertion des valeurs film_acteur
    for index, row in csv_film_actor.iterrows():
        try:
            cur.execute("""INSERT INTO film_actor (actor_id, film_id)
                VALUES (%s, %s)""", (int(row['actor_id']), int(row['film_id'])))
            print("Valeurs insérées avec succès.")
        except psycopg2.Error as e:
            print("Erreur lors de l'insertion des valeurs:", e)
            
    cur.close()
    conn.close()
            




