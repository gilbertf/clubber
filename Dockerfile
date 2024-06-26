# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
ADD /django-pwa /django-pwa
RUN pip install ../django-pwa/
RUN generateSecKey.sh /code/config/settings.yml
