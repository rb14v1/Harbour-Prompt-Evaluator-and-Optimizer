# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci || npm install || npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:1.27-alpine

RUN apk upgrade --no-cache

RUN printf 'server {\n    listen 0.0.0.0:8080;\n    server_name _;\n    root /usr/share/nginx/html;\n    index index.html;\n    location = /healthz {\n        access_log off;\n        default_type text/plain;\n        return 200 "ok";\n    }\n    location / {\n        try_files $uri $uri/ /index.html;\n    }\n}\n' > /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx must run unprivileged, so every path it writes to moves somewhere the nginx user owns.
RUN sed -i 's@^pid .*@pid /tmp/nginx.pid;@' /etc/nginx/nginx.conf \
 && sed -i '/^user /d' /etc/nginx/nginx.conf \
 && mkdir -p /tmp/nginx-cache \
 && chown -R nginx:nginx /tmp/nginx-cache /var/cache/nginx /usr/share/nginx/html

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:8080/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
