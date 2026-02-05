FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY . .

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN apk add --no-cache gettext

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/docker-entrypoint.sh"]
