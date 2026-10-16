# Sirve el frontend con nginx para desplegar en Coolify
FROM nginx:1.27-alpine

COPY . /usr/share/nginx/html
COPY docker/generar-config.sh /docker-entrypoint.d/40-generar-config.sh
RUN chmod +x /docker-entrypoint.d/40-generar-config.sh && rm -rf /usr/share/nginx/html/docker /usr/share/nginx/html/Dockerfile

EXPOSE 80
