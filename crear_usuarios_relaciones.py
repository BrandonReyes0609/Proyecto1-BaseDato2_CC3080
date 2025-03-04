from neo4j import GraphDatabase
import random
import config  # Importamos las credenciales desde config.py

# Conectar con Neo4j usando config.py
driver = GraphDatabase.driver(config.URI, auth=(config.USER, config.PASSWORD))

# Listas de valores aleatorios
NOMBRES = ["Carlos", "Ana", "Luis", "Sofía", "Jorge", "Marta", "Pedro", "Lucía", "Fernando", "Elena"]
APELLIDOS = ["Gómez", "Rodríguez", "Fernández", "Pérez", "López", "Díaz", "Martínez", "Romero", "Suárez", "Vargas"]
PAISES = ["Guatemala", "México", "Argentina", "España", "Chile", "Colombia", "Perú", "Venezuela", "Ecuador", "Uruguay"]

# Función para crear usuarios aleatorios
def crear_usuarios(tx, user_id):
    nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
    edad = random.randint(18, 65)
    pais = random.choice(PAISES)
    suscripcion_premium = random.choice([True, False])

    tx.run("""
        MERGE (u:Usuario {id: $id})
        SET u.nombre = $nombre, u.edad = $edad, u.pais = $pais, u.suscripcion_premium = $suscripcion_premium
    """, id=user_id, nombre=nombre, edad=edad, pais=pais, suscripcion_premium=suscripcion_premium)

# Función para conectar usuarios con películas vistas y calificadas
def conectar_usuario_pelicula(tx, user_id):
    tx.run("""
        MATCH (u:Usuario {id: $id}), (p:Pelicula)
        WITH u, p ORDER BY rand() LIMIT 3
        MERGE (u)-[:VIO {fecha: date("2024-02-26"), dispositivo: "Smartphone", duracion_vista: toInteger(rand() * 120)}]->(p)
        MERGE (u)-[:CALIFICO {puntuacion: toInteger(rand() * 10), comentario: "Muy buena", fecha: date("2024-02-26")}]->(p)
    """, id=user_id)

# Función para conectar usuarios con géneros favoritos
def conectar_usuario_genero(tx, user_id):
    tx.run("""
        MATCH (u:Usuario {id: $id}), (g:Genero)
        WITH u, g ORDER BY rand() LIMIT 2
        MERGE (u)-[:LE_GUSTA {nivel_preferencia: toInteger(rand() * 10), desde_fecha: date("2022-01-01")}]->(g)
    """, id=user_id)

# Función para conectar usuarios con actores y directores seguidos
def conectar_usuario_personas(tx, user_id):
    tx.run("""
        MATCH (u:Usuario {id: $id}), (a:Actor)
        WITH u, a ORDER BY rand() LIMIT 2
        MERGE (u)-[:SIGUE]->(a);
    """, id=user_id)
    
    tx.run("""
        MATCH (u:Usuario {id: $id}), (d:Director)
        WITH u, d ORDER BY rand() LIMIT 1
        MERGE (u)-[:SIGUE]->(d);
    """, id=user_id)

# Función para conectar usuarios con otros usuarios similares
def conectar_usuarios_similares(tx, user_id):
    tx.run("""
        MATCH (u1:Usuario {id: $id}), (u2:Usuario)
        WHERE u1 <> u2
        WITH u1, u2 ORDER BY rand() LIMIT 1     
        MERGE (u1)-[:SIMILAR_A {porcentaje_similitud: toInteger(rand() * 100)}]->(u2);
    """, id=user_id)

# Crear y conectar usuarios en Neo4j
with driver.session() as session:
    for user_id in range(1, 201):  # 200 usuarios
        session.execute_write(crear_usuarios, user_id)
        session.execute_write(conectar_usuario_pelicula, user_id)
        session.execute_write(conectar_usuario_genero, user_id)
        session.execute_write(conectar_usuario_personas, user_id)
        session.execute_write(conectar_usuarios_similares, user_id)

print("¡200 usuarios creados y conectados en Neo4j! 🚀")

# Cerrar conexión
driver.close()
