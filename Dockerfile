FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app
COPY . /usr/src/app

WORKDIR /usr/src/app/saasrest

RUN pip install -r ../requirements.txt
RUN pip install -r requirements.txt

RUN pip install psycopg2-binary

ARG SAAS_ENV="development"

RUN echo saasServer Dockerfile: $SAAS_ENV env

ARG PORT=9007

EXPOSE ${PORT}
EXPOSE 443

CMD ./run.sh
