FROM postgres:13-alpine

# Copy initialization scripts
COPY initdb/ /docker-entrypoint-initdb.d/

# Set permissions
RUN chmod a+r /docker-entrypoint-initdb.d/*

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1