from neo4j import GraphDatabase
import random

# Conectar con Neo4j (Asegúrate de tener un archivo config.py con las credenciales)
import config
driver = GraphDatabase.driver(config.URI, auth=(config.USER, config.PASSWORD))

# Valores aleatorios para completar datos
ESTILOS_DIRECCION = ["Ciencia Ficción", "Acción", "Drama", "Comedia", "Terror", "Suspenso"]
NACIONALIDADES = ["EEUU", "Canadá", "México", "España", "Francia", "Alemania", "Brasil", "Argentina"]
DESCRIPCIONES_GENERO = {
    "Acción": "Películas llenas de adrenalina y explosiones.",
    "Comedia": "Películas diseñadas para hacer reír.",
    "Drama": "Historias emocionales y profundas.",
    "Ciencia Ficción": "Exploraciones del futuro y tecnología avanzada.",
    "Terror": "Películas de miedo y suspenso."
}

# Rellenar datos aleatorios para Directores
def completar_directores(tx):
    tx.run("""
        MATCH (d:Director)
        SET d.edad = COALESCE(d.edad, toInteger(rand() * 40) + 30),
            d.estilo = COALESCE(d.estilo, $estilo),
            d.premios = COALESCE(d.premios, toInteger(rand() * 10)),
            d.años_experiencia = COALESCE(d.años_experiencia, toInteger(rand() * 30))
    """, estilo=random.choice(ESTILOS_DIRECCION))

# Rellenar datos aleatorios para Actores
def completar_actores(tx):
    tx.run("""
        MATCH (a:Actor)
        SET a.edad = COALESCE(a.edad, toInteger(rand() * 40) + 20),
            a.nacionalidad = COALESCE(a.nacionalidad, $nacionalidad),
            a.peliculas_participadas = COALESCE(a.peliculas_participadas, toInteger(rand() * 50)),
            a.premios_ganados = COALESCE(a.premios_ganados, toInteger(rand() * 5))
    """, nacionalidad=random.choice(NACIONALIDADES))

# Rellenar datos aleatorios para Géneros
def completar_generos(tx):
    tx.run("""
        MATCH (g:Genero)
        SET g.descripcion = COALESCE(g.descripcion, $descripcion),
            g.popularidad = COALESCE(g.popularidad, toInteger(rand() * 10) + 1),
            g.recomendado_para_edades = COALESCE(g.recomendado_para_edades, [12, 18, 25]),
            g.activo = COALESCE(g.activo, true)
    """, descripcion=random.choice(list(DESCRIPCIONES_GENERO.values())))

# Ejecutar las funciones
with driver.session() as session:
    session.execute_write(completar_directores)
    session.execute_write(completar_actores)
    session.execute_write(completar_generos)

print("¡Datos aleatorios añadidos correctamente a los nodos!")

# Cerrar conexión
driver.close()
