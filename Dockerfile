# pull official base image
FROM tiangolo/uwsgi-nginx:python3.8-alpine

ENV UWSGI_INI uwsgi.ini

ENV STATIC_URL /app/staticfiles

WORKDIR /app
ADD . /app

RUN chmod g+w /app

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev vim

# install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

RUN python3 /app/manage.py collectstatic --noinput

ENV LISTEN_PORT 8000
EXPOSE 8000