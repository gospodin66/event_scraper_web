FROM python:3.12-slim

ARG FLASK_USER=webapp

RUN useradd --no-create-home --shell /bin/bash -u 1000 $FLASK_USER
RUN mkdir -p /app/html /app/static

RUN pip install --upgrade pip && pip install --no-cache-dir flask gunicorn celery paramiko sqlalchemy psycopg2-binary kafka-python flask_socketio gevent>=1.4 minio

WORKDIR /app

COPY event_scraper_celery/tasks.py /app/
COPY event_scraper_celery/celeryconfig.py /app/
COPY html/ /app/html/
COPY static/ /app/static/
COPY webserver.py /app/
COPY kafkaclient.py /app/
COPY minioclient.py /app/
COPY db.py /app/

RUN chown -R $FLASK_USER:$FLASK_USER /app
#USER $FLASK_USER

EXPOSE 5000
