FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=src.config.production

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY manage.py ./
COPY src ./src
RUN python manage.py collectstatic --noinput --settings=src.config.static_build

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER 10001

EXPOSE 10000
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn src.config.wsgi:application --config python:src.config.gunicorn_conf"]
