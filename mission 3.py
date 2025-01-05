from pymongo import MongoClient
import psycopg2

# Fonction pour la connexion à la base PostgreSQL
def connection_postgres(nom_bdd):
    return psycopg2.connect(
        database=nom_bdd,
        host="localhost",
        user="postgres",
        password="ldeloffr",
        port="5432"
    )

# Fonction pour récupérer les noms des colonnes d'une table
def table_colonnes(conn, nom_table):
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE nom_table = '{nom_table}';
        """)
        return [row[0] for row in cur.fetchall()]

# Fonction pour récupérer toutes les données d'une table
def recuperer_donnees_table(conn, nom_table):
    columns = table_colonnes(conn, nom_table)
    with conn.cursor() as cur:
        cur.execute(f"SELECT {', '.join(columns)} FROM {nom_table}")
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


if __name__ == "__main__":
    # Connexion à MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    bdd_mongo = client["ds_pagila"]
    
    nb_table = 5
    
    # Liste des bases PostgreSQL à migrer
    postgres_databases = [f"ds_pagila{n+1}" for n in range(nb_table)]
    
    # Migration des bases PostgreSQL vers MongoDB
    for nom_bdd_postgres in postgres_databases:
        postgres_to_mongodb(bdd_mongo, nom_bdd_postgres)
    
    print("Migration terminée avec succès.")
