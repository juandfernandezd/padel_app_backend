#!/bin/bash
export DISPLAY=:0
# Iniciar el daemon de pigpio
echo "Iniciando pigpio daemon..."
sudo pigpiod

# Ejecutar el servidor FastAPI
echo "Iniciando el servidor FastAPI..."
cd "$(dirname "$0")"
python3 ./main.py &

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

echo "Cerrando instancias existentes de Firefox..."
pkill -f firefox

# Crear un nuevo perfil temporal para Firefox
PROFILE_DIR=$(mktemp -d)
firefox --no-remote --profile "$PROFILE_DIR" --kiosk http://localhost:3000 &

# Limpiar el perfil temporal al salir
trap 'rm -rf "$PROFILE_DIR"' EXIT
