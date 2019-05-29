FROM nikolaik/python-nodejs:latest


ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app
COPY . /usr/src/app

WORKDIR /usr/src/app/saasrest

RUN pip install -r ../requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y gettext libgettextpo-dev

RUN pip install psycopg2-binary

RUN npm install -g mjml

ARG SAAS_ENV="development"

RUN echo saasServer Dockerfile: $SAAS_ENV env

ARG PORT=9007

EXPOSE ${PORT}
EXPOSE 443

CMD ./run.sh
