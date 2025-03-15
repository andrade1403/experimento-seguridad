# Usamos una imagen de Python
FROM python:3.12.4-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos
COPY . .
# Instalamos las dependencias
RUN pip install -r requirements.txt

# Exponemos el puerto en el que corre Flask
EXPOSE 5000

# Ejecutamos el microservicio
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]