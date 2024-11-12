# Usar una imagen base de Miniconda
FROM continuumio/miniconda3

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo environment.yml al contenedor
COPY environment.yml .

# Crear el entorno de Conda y activarlo
RUN conda env create -f environment.yml

# Activar el entorno y establecerlo como el entorno predeterminado
RUN echo "source activate crud_app" > ~/.bashrc
ENV PATH /opt/conda/envs/crud_app/bin:$PATH

# Copiar el resto de los archivos de la aplicación al contenedor
COPY . .

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]