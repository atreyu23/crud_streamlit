import streamlit as st
from snowflake.snowpark import Session
from dotenv import load_dotenv
import os

image_path = 'images/image1.jpg'
st.image(image_path)