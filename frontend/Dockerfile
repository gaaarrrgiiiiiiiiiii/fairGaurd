# Stage 1: Build
FROM node:20-slim AS builder
WORKDIR /app

# Accept backend URL at build time (Vite bakes it into the static bundle)
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json package-lock.json ./
RUN npm ci --silent

COPY . .
RUN npm run build


# Stage 2: Serve with nginx
FROM nginx:1.27-alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html

# Write nginx config with PORT placeholder
RUN printf 'server {\n  listen NGINX_PORT;\n  root /usr/share/nginx/html;\n  index index.html;\n  location / {\n    try_files $uri $uri/ /index.html;\n  }\n  location /health {\n    return 200 "ok";\n    add_header Content-Type text/plain;\n  }\n}\n' > /etc/nginx/conf.d/default.conf

# Cloud Run injects $PORT — substitute it into nginx config at container start
CMD sh -c "sed -i s/NGINX_PORT/${PORT:-80}/g /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
