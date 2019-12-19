FROM nikolaik/python-nodejs:latest

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app/saasrest
COPY saasrest/requirements.txt /usr/src/app/saasrest

WORKDIR /usr/src/app/saasrest

RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y gettext libgettextpo-dev
RUN pip install psycopg2-binary
RUN npm install -g mjml

ARG SAAS_ENV="development"

ARG PORT=9007
EXPOSE ${PORT}
EXPOSE 443

CMD ./run.sh
