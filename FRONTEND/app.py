import streamlit as st
import requests

# Configuración de la API
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Recomendador de Películas", page_icon="🎬", layout="wide")

st.markdown(
    """
    <h1 style="text-align: center;">🎥 Recomendador de Películas con IA</h1>
    <p style="text-align: center; font-size: 18px;">
        Descubre nuevas películas basadas en tus gustos y similitudes con otros usuarios.
    </p>
    """, unsafe_allow_html=True
)

user_id = st.text_input("🎭 Introduce tu ID de usuario:", placeholder="Ejemplo: 123")
option = st.selectbox("📌 Selecciona una acción:",
                      ["Obtener recomendaciones", "Consultar películas vistas", "Consultar relaciones de usuario",
                       "Eliminar usuario", "Eliminar película", "Eliminar relación específica", "Eliminar todas las relaciones"])

def obtener_peliculas_usuario(user_id):
    response = requests.get(f"{API_URL}/usuario/{user_id}/peliculas")
    return response.json().get("peliculas", []) if response.status_code == 200 else []

def obtener_relaciones_usuario(user_id):
    response = requests.get(f"{API_URL}/usuario/{user_id}/relaciones")
    return response.json().get("relaciones", []) if response.status_code == 200 else []

if user_id.isdigit():
    user_id = int(user_id)

    if option == "Obtener recomendaciones":
        rec_option = st.radio("📌 Método de recomendación:", ["Usuarios similares", "Géneros favoritos", "Actores seguidos"])
        if st.button("Ejecutar acción"):
            endpoint = f"{API_URL}/recomendaciones/{user_id}" if rec_option == "Usuarios similares" \
                else f"{API_URL}/recomendaciones/genero/{user_id}" if rec_option == "Géneros favoritos" \
                else f"{API_URL}/recomendaciones/actor/{user_id}"
            response = requests.get(endpoint)
            data = response.json().get("recomendaciones", []) if response.status_code == 200 else []
            if data:
                st.markdown(f"<h2>📌 Películas recomendadas para el usuario {user_id}</h2>", unsafe_allow_html=True)
                for pelicula in data:
                    st.markdown(f"### 🎞️ {pelicula['titulo']}")
            else:
                st.warning("⚠️ No encontramos recomendaciones para este usuario.")

    elif option == "Consultar películas vistas":
        peliculas = obtener_peliculas_usuario(user_id)
        st.write("🎬 Películas vistas:", peliculas if peliculas else "No se encontraron películas.")

    elif option == "Consultar relaciones de usuario":
        relaciones = obtener_relaciones_usuario(user_id)
        st.write("🔗 Relaciones del usuario:", relaciones if relaciones else "No se encontraron relaciones.")

    elif option == "Eliminar película":
        peliculas = obtener_peliculas_usuario(user_id)
        if peliculas:
            pelicula_seleccionada = st.selectbox("🎬 Selecciona la película a eliminar:", peliculas)
            if st.button("Eliminar película"):
                response = requests.delete(f"{API_URL}/pelicula/{pelicula_seleccionada}")
                if response.status_code == 200:
                    st.success(response.json().get("mensaje", "Operación exitosa"))
                else:
                    error_msg = response.json().get("detail", "Error desconocido")
                    st.error(error_msg)
        else:
            st.warning("⚠️ No se encontraron películas asociadas al usuario.")

    elif option == "Eliminar relación específica":
        relaciones = obtener_relaciones_usuario(user_id)
        if relaciones:
            relacion_seleccionada = st.selectbox("🔗 Selecciona la relación a eliminar:", relaciones)
            if st.button("Eliminar relación"):
                response = requests.delete(f"{API_URL}/usuario/{user_id}/relacion/{relacion_seleccionada}")
                if response.status_code == 200:
                    st.success(response.json().get("mensaje", "Operación exitosa"))
                else:
                    error_msg = response.json().get("detail", "Error desconocido")
                    st.error(error_msg)
        else:
            st.warning("⚠️ No se encontraron relaciones asociadas al usuario.")

    elif option == "Eliminar usuario":
        if st.button("Eliminar usuario"):
            response = requests.delete(f"{API_URL}/usuario/{user_id}")
            if response.status_code == 200:
                    st.success(response.json().get("mensaje", "Operación exitosa"))
            else:
                error_msg = response.json().get("detail", "Error desconocido")
                st.error(error_msg)

    elif option == "Eliminar todas las relaciones":
        if st.button("Eliminar todas las relaciones"):
            response = requests.delete(f"{API_URL}/usuario/{user_id}/relaciones")
            if response.status_code == 200:
                st.success(response.json().get("mensaje", "Operación exitosa"))
            else:
                error_msg = response.json().get("detail", "Error desconocido")
                st.error(error_msg)
else:
    st.warning("⚠️ Ingresa un ID numérico válido.")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>🔹 Recomendaciones generadas con <strong>Neo4j</strong> y <strong>FastAPI</strong> 🚀</p>", unsafe_allow_html=True)
