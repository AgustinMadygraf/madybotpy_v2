# Usa una imagen base de Python con Linux
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el contenido de tu proyecto al contenedor
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto 5000 para Waitress/Gunicorn
EXPOSE 5000

# Comando para iniciar tu aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
