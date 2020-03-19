FROM python:3.7.5-slim-buster

ENV INSTALL_PATH /block_chain
RUN mkdir -p $INSTALL_PATH
RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends
RUN apt-get install -y  gcc python3-dev musl-dev --no-install-recommends
WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .
CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "block_chain.app:create_app()"
