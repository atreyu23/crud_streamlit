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
    image_filenames = [os.path.basename(url) for url in image_urls]
    selected_image = st.selectbox("Selecciona una imagen:", image_filenames)
    
    if selected_image:
        selected_image_url = image_urls[image_filenames.index(selected_image)]
        st.image(selected_image_url, caption="Imagen seleccionada", use_column_width=True)
        return selected_image, selected_image_url

# Función para obtener etiquetas de la imagen
def get_tags_for_image(image_url):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Obtener el ID de la imagen
        cursor.execute("SELECT ID FROM images WHERE image_url = %s", (image_url,))
        image_id = cursor.fetchone()[0]

        # Obtener las etiquetas asociadas a la imagen
        cursor.execute("""
            SELECT t.TAG 
            FROM TAGS t
            JOIN IMAGE_TAGS it ON t.ID = it.TAG_ID
            WHERE it.IMAGE_ID = %s
        """, (image_id,))
        tags = cursor.fetchall()
        return [row[0] for row in tags]
    finally:
        cursor.close()
        conn.close()

# Función para mostrar etiquetas en formato "tag"
def display_tags(tags):
    if tags:
        st.subheader("Etiquetas asignadas:")
        for tag in tags:
            # Mostrar cada etiqueta como un "tag" con una "X"
            st.markdown(f'<span style="background-color: #e0e0e0; padding: 5px; border-radius: 5px;">{tag} <span style="color: red; cursor: pointer;">X</span></span>', unsafe_allow_html=True)
    else:
        st.write("No hay etiquetas asignadas a esta imagen.")

# Función para agregar etiqueta a la imagen
def add_tag_to_image(image_url, tag):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Verificar si la etiqueta ya existe
        cursor.execute("SELECT ID FROM TAGS WHERE TAG = %s", (tag,))
        tag_result = cursor.fetchone()

        if tag_result:
            tag_id = tag_result[0]  # Obtener el ID de la etiqueta existente
        else:
            # Si no existe, insertarla en la tabla TAGS
            cursor.execute("INSERT INTO TAGS (TAG) VALUES (%s)", (tag,))
            conn.commit()
            # Obtener el ID de la etiqueta recién creada
            cursor.execute("SELECT ID FROM TAGS WHERE TAG = %s", (tag,))
            tag_id = cursor.fetchone()[0]

        # Obtener el ID de la imagen
        cursor.execute("SELECT ID FROM images WHERE image_url = %s", (image_url,))
        image_id = cursor.fetchone()[0]

        # Verificar si la etiqueta ya está asignada a la imagen
        cursor.execute("SELECT * FROM IMAGE_TAGS WHERE IMAGE_ID = %s AND TAG_ID = %s", (image_id, tag_id))
        existing_assignment = cursor.fetchone()

        if existing_assignment:
            st.warning("La etiqueta ya está asignada a esta imagen.")
        else:
            # Insertar en la tabla IMAGE_TAGS
            cursor.execute("INSERT INTO IMAGE_TAGS (IMAGE_ID, TAG_ID) VALUES (%s, %s)", (image_id, tag_id))
            conn.commit()
            st.success("Etiqueta añadida exitosamente a la imagen.")
        
    finally:
        cursor.close()
        conn.close()

def main():
    st.title("Aplicación CRUD con Streamlit y Snowflake")
    
    # Obtener las imágenes
    image_urls = get_images()
    
    # Mostrar el selector de imágenes
    if image_urls:
        selected_image, selected_image_url = display_image_selector(image_urls)
        
        # Mostrar etiquetas de la imagen seleccionada
        if selected_image_url:
            tags = get_tags_for_image(selected_image_url)
            display_tags(tags)  # Llamar a la función para mostrar las etiquetas

            new_tag = st.text_input("Añadir nueva etiqueta:")

            if st.button("Añadir etiqueta"):
                if new_tag:
                    add_tag_to_image(selected_image_url, new_tag)  # Función para añadir la etiqueta
                    
                    # Recargar la página para mostrar la imagen seleccionada con etiquetas actualizadas
                    st.rerun()  # Recargar la aplicación

if __name__ == "__main__":
    main()