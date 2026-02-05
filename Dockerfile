#imagen de python ligera
FROM python:3.10-slim

#Evitamos que python genere arhivos .pyc y forzamoslogs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

#Copiamos los requirements e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Copiamos el resto de codigo
COPY . .

#Exponemos el puerto de Streamlit
EXPOSE 8501

#Verificacion de salud
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

#Comando para arrancar la aplicacion
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

