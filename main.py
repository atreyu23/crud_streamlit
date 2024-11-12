import streamlit as st
from snowflake.snowpark import Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Snowflake connection parameters
connection_parameters = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_ROLE")
}

# Create a Snowflake session
session = Session.builder.configs(connection_parameters).create()

# Function to set database and schema
def set_database_and_schema(database, schema):
    session.sql(f"USE DATABASE {database}").collect()
    session.sql(f"USE SCHEMA {schema}").collect()

# Function to fetch image URLs from Snowflake
def fetch_image_urls(table_name):
    query = f"SELECT ID, IMAGE_URL FROM {table_name} LIMIT 10"
    return session.sql(query).collect()

# Function to fetch tags for a given image ID
def fetch_tags_for_image(image_id):
    query = f"""
    SELECT T.ID, T.TAG 
    FROM TAGS T
    JOIN IMAGE_TAGS IT ON T.ID = IT.TAG_ID
    WHERE IT.IMAGE_ID = {image_id}
    """
    return session.sql(query).collect()

# Function to delete a tag for a given image ID
def delete_tag(image_id, tag_id):
    query = f"DELETE FROM IMAGE_TAGS WHERE IMAGE_ID = {image_id} AND TAG_ID = {tag_id}"
    session.sql(query).collect()

# Function to insert a new tag for a given image ID
def insert_tag(image_id, tag):
    # Check if the tag already exists
    tag_check_query = f"SELECT ID FROM TAGS WHERE TAG = '{tag}'"
    tag_check_result = session.sql(tag_check_query).collect()

    if tag_check_result:
        # Tag exists, get the existing ID
        tag_id_value = tag_check_result[0][0]
    else:
        # Tag doesn't exist, insert it
        insert_tag_query = f"INSERT INTO TAGS (TAG) VALUES ('{tag}')"
        tag_id_result = session.sql(insert_tag_query).collect()
        tag_id_value = tag_id_result[0][0]  # Get the new tag ID

    # Now, insert the tag ID into the IMAGE_TAGS table
    insert_image_tag_query = f"""
    INSERT INTO IMAGE_TAGS (IMAGE_ID, TAG_ID)
    VALUES ({image_id}, {tag_id_value})
    """
    session.sql(insert_image_tag_query).collect()

# Streamlit app layout
st.title("Image Display from Snowflake")

# Input for database and schema
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")

# Set the database and schema
set_database_and_schema(database, schema)

# Set the table name directly
table_name = "IMAGES"

# Fetch and display images
image_data = fetch_image_urls(table_name)

# Convert the fetched data to a list of image paths and IDs
image_paths = [(row[0], row[1]) for row in image_data]

# Check if there are images to display
if image_paths:
    # Extract just the image file names for the dropdown
    image_names = [os.path.basename(path[1]) for path in image_paths]
    
    # Create a dropdown selector for images
    selected_image_name = st.selectbox("Select an image to display:", image_names)
    
    # Get the full path and ID of the selected image
    selected_image_index = image_names.index(selected_image_name)
    selected_image_id = image_paths[selected_image_index][0]
    selected_image_path = image_paths[selected_image_index][1]
    
    # Display the selected image
    if os.path.exists(selected_image_path):
        st.image(selected_image_path, caption="Selected Image", use_column_width=True)
        
        # Fetch and display tags for the selected image
        tags = fetch_tags_for_image(selected_image_id)
        tag_list = [(tag[0], tag[1]) for tag in tags]  # List of tuples (ID, TAG)
        
        # Show existing tags as clickable labels
        st.subheader("Tags:")
        for tag_id, tag in tag_list:
            if st.button(f"❌ {tag}", key=f"delete_{tag_id}"):  # Agregar un key único
                delete_tag(selected_image_id, tag_id)
                st.success(f"Tag '{tag}' deleted successfully.")
                st.rerun()  # Refresh the app to show updated tags

        # Input for adding a new tag
        new_tag = st.text_input("Add a new tag:")
        if st.button("Add Tag"):
            if new_tag:
                insert_tag(selected_image_id, new_tag)
                st.success(f"Tag '{new_tag}' added successfully.")
                st.rerun()  # Refresh the app to show the new tag