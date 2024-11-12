import streamlit as st
import os
import snowflake.connector
from config import *

# Establecer la conexión a Snowflake
def create_connection():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE  # Añadir el rol
    )
    return conn

# Función para obtener imágenes de la tabla 'images'
def get_images():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_url FROM images")
        images = cursor.fetchall()
        image_urls = [row[0] for row in images]
        return image_urls
    finally:
        cursor.close()
        conn.close()

# Función para mostrar un selector de imágenes
def display_image_selector(image_urls):
    # Extraer solo los nombres de los archivos
    image_filenames = [os.path.basename(url) for url in image_urls]
    selected_image = st.selectbox("Selecciona una imagen:", image_filenames)
    
    # Obtener la URL completa del archivo seleccionado
    if selected_image:
        selected_image_url = image_urls[image_filenames.index(selected_image)]
        st.image(selected_image_url, caption="Imagen seleccionada", use_column_width=True)

def main():
    st.title("Aplicación CRUD con Streamlit y Snowflake")
    
    # Obtener las imágenes
    image_urls = get_images()
    
    # Mostrar el selector de imágenes
    if image_urls:
        display_image_selector(image_urls)
    else:
        st.write("No se encontraron imágenes.")

if __name__ == "__main__":
    main()