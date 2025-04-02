FROM nginx:1.23-alpine

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configuration
COPY nginx.conf /etc/nginx/conf.d/fitness_app.conf

# Copy static files
COPY --from=builder /app/staticfiles /usr/share/nginx/html/static

# Copy custom error pages
COPY error_pages/ /usr/share/nginx/html/error_pages/

# Create cache directory and set permissions
RUN mkdir -p /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/run && \
    chown -R nginx:nginx /usr/share/nginx/html

USER nginx

EXPOSE 8080