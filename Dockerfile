FROM python:3.12

RUN apt-get update && apt-get install -y postgresql-client

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_CREATE=false 

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . /app