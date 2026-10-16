#!/bin/sh
# Al arrancar el contenedor escribe js/config.js con la URL de la API
# que se configura en Coolify en la variable API_URL.
if [ -n "$API_URL" ]; then
  echo "const API_URL = \"$API_URL\";" > /usr/share/nginx/html/js/config.js
  echo "config.js generado con API_URL=$API_URL"
fi
