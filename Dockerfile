# -----
FROM rust:1.62 AS smsagent-build
WORKDIR /build/smsagent
COPY smsagent/Cargo.lock .
COPY smsagent/Cargo.toml .
RUN mkdir .cargo && cargo vendor > .cargo/config
COPY smsagent /build/smsagent
RUN cargo build --release

# -----
FROM rust:1.62 AS chat-build
WORKDIR /build/chat
COPY chat/Cargo.lock .
COPY chat/Cargo.toml .
RUN mkdir .cargo && cargo vendor > .cargo/config
COPY chat /build/chat
RUN cargo build --release

# -----
FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/archive.ubuntu.com/mirrors.tencent.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.tencent.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y python3-pip python3-venv locales dnsutils iproute2 netcat tini runit && \
    locale-gen zh_CN.UTF-8 && \
    pip3 install -U pip poetry gunicorn && \
    poetry config virtualenvs.create false && \
    true

ENV TERM xterm
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN:en
ENV LC_ALL zh_CN.UTF-8

# -----
FROM base AS backend

WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/poetry.lock ./
RUN poetry install --no-dev
ADD backend /app
CMD ["tini", "/bin/bash", "--", "-c", "exec poetry run gunicorn -w 4 --reuse-port backend.wsgi"]


# -----
FROM base AS game

WORKDIR /app
COPY src/pyproject.toml ./
COPY src/poetry.lock ./
RUN poetry install --no-dev
ADD src /app
CMD ["tini", "/bin/bash", "--", "-c", "exec poetry run python3 start_server.py $INSTANCE --log='file:///data/thb/server.log?level=INFO' --backend $BACKEND_URL --archive-path /data/thb/archive --interconnect \"$INTERCONNECT_URL\""]

# # -----
# FROM base AS smsagent
# WORKDIR /app
# COPY --from=smsagent-build /build/smsagent/target/release/smsagent /app/smsagent
# CMD ["tini", "/app/smsagent"]


# -----
FROM base AS chat
WORKDIR /app
COPY --from=chat-build /build/chat/target/release/chat /app/chat
CMD ["tini", "/bin/bash", "--", "-c", "exec /app/chat --backend $BACKEND_URL"]