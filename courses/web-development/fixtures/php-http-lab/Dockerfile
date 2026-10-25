FROM php:8.4.27-cli-bookworm

RUN php -r 'exit(extension_loaded("pdo_sqlite") ? 0 : 1);' \
    && groupadd --gid 10001 webstudy \
    && useradd --uid 10001 --gid 10001 --no-create-home webstudy \
    && mkdir -p /app/public /data/sessions \
    && chown -R 10001:10001 /app /data \
    && chmod 700 /data /data/sessions
COPY --chown=10001:10001 public/ /app/public/
USER 10001:10001
WORKDIR /app
EXPOSE 8080
CMD ["php", "-d", "display_errors=0", "-d", "log_errors=1", "-d", "post_max_size=4K", "-d", "upload_max_filesize=1K", "-d", "max_execution_time=10", "-S", "0.0.0.0:8080", "-t", "/app/public", "/app/public/index.php"]
