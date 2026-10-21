FROM nginx:1.27

RUN rm -f /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY site.conf /etc/nginx/conf.d/10-site.conf
COPY render-upstreams.sh /opt/nginx/render-upstreams.sh
COPY entrypoint.sh /opt/nginx/entrypoint.sh

RUN chmod +x /opt/nginx/render-upstreams.sh /opt/nginx/entrypoint.sh

ENTRYPOINT ["/opt/nginx/entrypoint.sh"]
