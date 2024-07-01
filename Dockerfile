# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine AS builder

RUN <<EOF
apk update
apk add git
apk add gcc g++ musl-dev graphviz
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# install Docker tools (cli, buildx, compose)
# COPY --from=gloursdocker/docker / /

# Copy .env file to /src folder
COPY .env /src/.env

WORKDIR /src

COPY ./src/requirements.txt /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY ./src/generate_pipeline.py /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install numpy scikit-learn

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install git+https://github.com/hyperopt/hyperopt-sklearn


RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install svgwrite

COPY ../example /src/example

COPY ./src/. .

ENV FLASK_SERVER_PORT=9000

EXPOSE 9000

CMD ["python3", "server.py"]
