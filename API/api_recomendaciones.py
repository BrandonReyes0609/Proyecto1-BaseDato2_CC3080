from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
import config

# Inicializar la aplicación FastAPI
app = FastAPI()

# Conectar con Neo4j
driver = GraphDatabase.driver(config.URI, auth=(config.USER, config.PASSWORD))

# 🔹 Obtener recomendaciones por usuarios similares
def obtener_recomendaciones(tx, user_id):
    query = """
    MATCH (u1:Usuario {id: $user_id})-[:SIMILAR_A]->(u2:Usuario)-[v:VIO]->(p:Pelicula)
    WHERE NOT (u1)-[:VIO]->(p)
    RETURN p.titulo AS PeliculaRecomendada, count(*) AS Frecuencia, avg(v.duracion_vista) AS TiempoPromedio
    ORDER BY Frecuencia DESC, TiempoPromedio DESC
    LIMIT 5;
    """
    result = tx.run(query, user_id=user_id)
    return [{"titulo": record["PeliculaRecomendada"], "frecuencia": record["Frecuencia"], "tiempo_promedio": record["TiempoPromedio"]} for record in result]

# 🔹 Obtener recomendaciones por género
def obtener_recomendaciones_por_genero(tx, user_id):
    query = """
    MATCH (u:Usuario {id: $user_id})-[:LE_GUSTA]->(g:Genero)<-[:PERTENECE_A]-(p:Pelicula)
    WHERE NOT (u)-[:VIO]->(p)
    RETURN p.titulo AS PeliculaRecomendada, g.nombre AS Genero, count(*) AS Frecuencia
    ORDER BY Frecuencia DESC
    LIMIT 5;
    """
    result = tx.run(query, user_id=user_id)
    return [{"titulo": record["PeliculaRecomendada"], "genero": record["Genero"], "frecuencia": record["Frecuencia"]} for record in result]

# 🔹 Obtener recomendaciones por actor seguido
def obtener_recomendaciones_por_actor(tx, user_id):
    query = """
    MATCH (u:Usuario {id: $user_id})-[:SIGUE]->(a:Actor)<-[:PROTAGONIZADA_POR]-(p:Pelicula)
    WHERE NOT (u)-[:VIO]->(p)
    RETURN p.titulo AS PeliculaRecomendada, a.nombre AS Actor, count(*) AS Frecuencia
    ORDER BY Frecuencia DESC
    LIMIT 5;
    """
    result = tx.run(query, user_id=user_id)
    return [{"titulo": record["PeliculaRecomendada"], "actor": record["Actor"], "frecuencia": record["Frecuencia"]} for record in result]


# 🔹 Eliminar una relación específica de un usuario
def eliminar_relacion_especifica(tx, user_id, relacion):
    query = """
    MATCH (u:Usuario {id: $user_id})-[r:`""" + relacion + """`]->() DELETE r RETURN COUNT(r) AS eliminados;
    """
    result = tx.run(query, user_id=user_id)
    return result.single()["eliminados"]

# 🔹 Eliminar todas las relaciones de un usuario
def eliminar_todas_relaciones(tx, user_id):
    query = """
    MATCH (u:Usuario {id: $user_id})-[r]-() DELETE r RETURN COUNT(r) AS eliminados;
    """
    result = tx.run(query, user_id=user_id)
    return result.single()["eliminados"]

# 🔹 Endpoints para obtener recomendaciones
@app.get("/recomendaciones/{user_id}")
def recomendaciones(user_id: int):
    with driver.session() as session:
        peliculas = session.execute_read(obtener_recomendaciones, user_id)
    return {"usuario": user_id, "recomendaciones": peliculas}

@app.get("/recomendaciones/genero/{user_id}")
def recomendaciones_por_genero(user_id: int):
    with driver.session() as session:
        peliculas = session.execute_read(obtener_recomendaciones_por_genero, user_id)
    return {"usuario": user_id, "recomendaciones": peliculas}

@app.get("/recomendaciones/actor/{user_id}")
def recomendaciones_por_actor(user_id: int):
    with driver.session() as session:
        peliculas = session.execute_read(obtener_recomendaciones_por_actor, user_id)
    return {"usuario": user_id, "recomendaciones": peliculas}

# 🔹 Obtener películas vistas por un usuario
@app.get("/usuario/{user_id}/peliculas")
def obtener_peliculas_usuario(user_id: int):
    with driver.session() as session:
        result = session.run("MATCH (u:Usuario {id: $user_id})-[:VIO]->(p:Pelicula) RETURN p.titulo AS titulo", {"user_id": user_id})
        peliculas = [record["titulo"] for record in result]
    return {"peliculas": peliculas} if peliculas else {"peliculas": []}

# 🔹 Obtener relaciones de un usuario
@app.get("/usuario/{user_id}/relaciones")
def obtener_relaciones_usuario(user_id: int):
    with driver.session() as session:
        result = session.run("MATCH (u:Usuario {id: $user_id})-[r]-() RETURN DISTINCT type(r) AS relacion", {"user_id": user_id})
        relaciones = [record["relacion"] for record in result]
    return {"relaciones": relaciones} if relaciones else {"relaciones": []}

# 🔹 Eliminar una película por su nombre
@app.delete("/pelicula/{titulo}")
def eliminar_pelicula(titulo: str):
    with driver.session() as session:
        result = session.run("MATCH (p:Pelicula {titulo: $titulo}) DETACH DELETE p RETURN COUNT(p) AS eliminados", {"titulo": titulo})
        if result.single()["eliminados"] == 0:
            raise HTTPException(status_code=404, detail="Película no encontrada.")
    return {"mensaje": f"Película '{titulo}' eliminada correctamente"}

# 🔹 Eliminar un usuario y todas sus relaciones
@app.delete("/usuario/{user_id}")
def eliminar_usuario(user_id: int):
    with driver.session() as session:
        result = session.run("MATCH (u:Usuario {id: $user_id}) DETACH DELETE u", user_id=user_id)
        if result.consume().counters.nodes_deleted == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": f"Usuario con ID {user_id} eliminado correctamente"}

@app.delete("/usuario/{user_id}/relacion/{relacion}")
def eliminar_relacion(user_id: int, relacion: str):
    with driver.session() as session:
        eliminados = session.execute_write(eliminar_relacion_especifica, user_id, relacion)
        if eliminados == 0:
            raise HTTPException(status_code=404, detail=f"No se encontró la relación '{relacion}' para el usuario {user_id}.")
    return {"mensaje": f"Relación '{relacion}' eliminada correctamente para el usuario {user_id}"}


@app.delete("/usuario/{user_id}/relaciones")
def eliminar_todas_relaciones_usuario(user_id: int):
    with driver.session() as session:
        eliminados = session.execute_write(eliminar_todas_relaciones, user_id)
        if eliminados == 0:
            raise HTTPException(status_code=404, detail=f"No se encontraron relaciones para el usuario {user_id}.")
    return {"mensaje": f"Todas las relaciones del usuario {user_id} han sido eliminadas correctamente"}

# 🔹 Cerrar conexión con Neo4j cuando la API se detiene
@app.on_event("shutdown")
def cerrar_conexion():
    driver.close()