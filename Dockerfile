ARG PYTHON_VERSION=3.13-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code
ENV DATABASE_URL "sqlite://:memory:"
ENV SECRET_KEY "iJtvIwzWpK59lw35BtLgfwJVNa0xNjP99dslXHZoe2Bz6Qjynh"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","--workers","2","squashvote.wsgi"]
