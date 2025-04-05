FROM python:3.12-slim

ARG CELERY_USER=celery

RUN apt update && apt install -y \
    openssh-client

RUN useradd --no-create-home --shell /bin/bash $CELERY_USER

WORKDIR /app

RUN pip install --upgrade pip && pip install --no-cache-dir celery paramiko kafka-python

COPY celeryconfig.py /app/
COPY tasks.py /app/

RUN chown -R $CELERY_USER:$CELERY_USER /app

#USER $CELERY_USER

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]