#!/bin/bash

# Iniciar el daemon de pigpio
echo "Iniciando pigpio daemon..."
sudo pigpiod

# Ejecutar el servidor FastAPI
echo "Iniciando el servidor FastAPI..."
cd "$(dirname "$0")"
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Esperar un momento para asegurarse de que el servidor FastAPI ha iniciado
sleep 5

# Exportar la variable de entorno
echo "Exportando variable NODE_OPTIONS..."
export NODE_OPTIONS=--openssl-legacy-provider

# Ejecutar la aplicación React
echo "Iniciando la aplicación React..."
cd ../padel_app_frontend
npm start &

# Esperar un momento para asegurarse de que la aplicación React ha iniciado
sleep 10

# Abrir Firefox en modo pantalla completa apuntando a la aplicación React
echo "Abriendo Firefox en modo pantalla completa..."
firefox --kiosk http://localhost:3000
