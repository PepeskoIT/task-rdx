FROM python:3.10-slim

ARG APP_PATH
RUN echo $APP_PATH
RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH

RUN apt-get clean \
    && apt-get update \
    && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/cache/apt

RUN pip3 install pipenv 
COPY sync/Pipfile sync/Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

COPY sync/src/ .
COPY docker/sync/entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/bin/sh", "./entrypoint.sh"]