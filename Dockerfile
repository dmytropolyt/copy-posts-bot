FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

COPY ./src /app
COPY ./requirements.txt /tmp/requirements.txt

WORKDIR /app

RUN apk add --update --no-cache --virtual .tmp-build-deps build-base musl-dev  \
      libffi-dev openssl-dev cargo pkgconfig &&  \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    apk del .tmp-build-deps