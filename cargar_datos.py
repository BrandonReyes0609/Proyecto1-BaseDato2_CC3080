from neo4j import GraphDatabase
import pandas as pd
from datetime import datetime
import config  # Archivo separado para credenciales

# Conectar con Neo4j
driver = GraphDatabase.driver(config.URI, auth=(config.USER, config.PASSWORD))

# Cargar el archivo CSV
movies_df = pd.read_csv("movies.csv")

# Función para convertir fecha a formato YYYY-MM-DD
def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None  # Si la fecha es inválida

# Aplicar la conversión de fechas
movies_df["release_date"] = movies_df["release_date"].apply(format_date)

def insert_data(tx, movie):
    fecha_estreno = movie["release_date"]

    # Crear nodo de película
    tx.run("""
        MERGE (p:Pelicula {id: $id})
        SET p.titulo = $titulo, p.año = $año, p.calificacion = $calificacion,
            p.fecha_estreno = date($fecha_estreno), p.duracion = $duracion
    """, id=int(movie["id"]), titulo=movie["original_title"], año=int(movie["release_year"]),
         calificacion=float(movie["vote_average"]), fecha_estreno=fecha_estreno, duracion=int(movie["runtime"]))

    # Crear géneros y establecer relaciones
    for genero in str(movie["genres"]).split("|"):
        genero = genero.strip()
        if genero:
            tx.run("""
                MERGE (g:Genero {nombre: $genero})
                WITH g
                MATCH (p:Pelicula {id: $id})
                MERGE (p)-[:PERTENECE_A]->(g)
            """, genero=genero, id=int(movie["id"]))

    # Crear actores y establecer relaciones
    for actor in str(movie["cast"]).split("|"):
        actor = actor.strip()
        if actor:
            tx.run("""
                MERGE (a:Actor {nombre: $actor})
                WITH a
                MATCH (p:Pelicula {id: $id})
                MERGE (p)-[:PROTAGONIZADA_POR]->(a)
            """, actor=actor, id=int(movie["id"]))

    # **Manejar director con seguridad para evitar errores**
    director = str(movie["director"]).strip() if pd.notna(movie["director"]) else None
    if director:
        tx.run("""
            MERGE (d:Director {nombre: $director})
            WITH d
            MATCH (p:Pelicula {id: $id})
            MERGE (p)-[:DIRIGIDA_POR]->(d)
        """, director=director, id=int(movie["id"]))

# Cargar los datos en Neo4j
with driver.session() as session:
    for _, movie in movies_df.iterrows():
        session.execute_write(insert_data, movie)

print("¡Datos cargados correctamente en Neo4j!")

# Cerrar conexión
driver.close()
