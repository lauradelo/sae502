from pymongo import MongoClient
import psycopg2
import pickle
import os
import schedule
import time


# Fichier de suivi pour garder la dernière base insérée
num_dernier_insert = "num_dernier_insert.pkl"

# Fonction pour lire la dernière base insérée
def dernier_insert():
    if os.path.exists(num_dernier_insert):
        with open(num_dernier_insert, "rb") as f:
            return pickle.load(f)
    return 0  # Si aucun suivi, commencer à partir de pagila1

# Fonction pour sauvegarder la dernière base insérée
def save_dernier_insert(last_inserted):
    with open(num_dernier_insert, "wb") as f:
        pickle.dump(last_inserted, f)

# Fonction pour se connecter à PostgreSQL
def connection_postgres(database_name):
    return psycopg2.connect(
        database=database_name,
        host="localhost",
        user="postgres",
        password="ldeloffr",
        port="5432"
    )

# Fonction pour récupérer les noms des colonnes d'une table
def table_colonnes(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}';
        """)
        return [row[0] for row in cur.fetchall()]

# Fonction pour récupérer les noms des tables
def nom_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name Z
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        return [row[0] for row in cur.fetchall()]

# Fonction pour détecter les bases de données "pagila" i>dernier_insert
def pagila_databases():
    conn = psycopg2.connect(
        database="postgres",  
        host="localhost",
        user="postgres",
        password="ldeloffr",
        port="5432"
    )
    with conn.cursor() as cur:
        cur.execute("""
            SELECT datname 
            FROM pg_database 
            WHERE datname LIKE 'ds_pagila%';
        """)
        # Filtrer les bases avec un numéro supérieur à dernier_insert
        databases = [
            row[0] for row in cur.fetchall() 
            if int(row[0].replace("ds_pagila", "")) > dernier_insert()
        ]
            
        return databases

# Fonction pour récupérer les données d'une table
def recuperer_donnees_table(conn, table_name):
    columns = table_colonnes(conn, table_name)
    with conn.cursor() as cur:
        cur.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]

# Fonction pour construire une structure imbriquée pour MongoDB
def construire_structure_film(conn):
    # Récupération des données des tables liées
    films = recuperer_donnees_table(conn, "film")
    film_actors = recuperer_donnees_table(conn, "film_actor")
    actors = recuperer_donnees_table(conn, "actor")

    # Création d'un dictionnaire d'actors pour un accès rapide
    actor_dict = {actor["actor_id"]: actor for actor in actors}

    # Construction des données imbriquées
    for film in films:
        film["actors"] = []
        for film_actor in film_actors:
            if film_actor["film_id"] == film["film_id"]:
                actor = actor_dict.get(film_actor["actor_id"])
                if actor:
                    film["actors"].append({
                        "actor_id": actor["actor_id"],
                        "first_name": actor["first_name"],
                        "last_name": actor["last_name"]
                    })
    return films

# Fonction pour migrer les données vers MongoDB
def postgres_to_mongodb(bdd_mongo, nom_bdd_postgres):
    conn = connection_postgres(nom_bdd_postgres)
    try:
        # Construction des films avec acteurs
        films = construire_structure_film(conn)

        # Insertion dans MongoDB
        if films:
            bdd_mongo["film"].insert_many(films)
            print(f"Données migrées pour la base {nom_bdd_postgres}.")
    except psycopg2.Error as e:
        print(f"Erreur lors de la migration depuis {nom_bdd_postgres} :", e)
    finally:
        conn.close()



# Fonction à exécuter toutes les semaines
def job():
    # Connexion à MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db_mongo = client["ds_pagila"]

    # Détection dynamique des bases de données pagila
    databases = pagila_databases()
    # Migration des données
    for db_postgres_name in databases:
        postgres_to_mongodb(db_mongo, db_postgres_name)
        # Sauvegarde de la dernière base insérée
        dernier_num = int(db_postgres_name.replace("ds_pagila", ""))
        save_dernier_insert(dernier_num)
    print("Migration des bases pagila terminée avec succès.")

# Planification de la tâche pour chaque vendredi à 14h
def schedule_weekly_task():
    schedule.every().friday.at("16:00").do(job)
    print("Tâche hebdomadaire programmée pour chaque vendredi à 16:00.")

# Fonction pour faire fonctionner le planificateur
def run_schedule():
    while True:
        schedule.run_pending()  # Exécute les tâches planifiées
        time.sleep(60)  # Attendre 1 minute avant la prochaine vérification


# Lancer la planification
if __name__ == "__main__":
    schedule_weekly_task()  # Planifier la tâche hebdomadaire
    run_schedule()  # Lancer la boucle de planification








