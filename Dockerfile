FROM python:3.8.2

RUN pip install pipenv

ENV PROJECT_DIR /usr/local/bin/src/app
WORKDIR ${PROJECT_DIR}

COPY Pipfile Pipfile.lock ${PROJECT_DIR}/
RUN pipenv install --system --deploy
COPY ./src .

RUN curl https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -o ngrok-stable-linux-amd64.zip
RUN unzip ngrok-stable-linux-amd64.zip

CMD ["python", "server.py"]