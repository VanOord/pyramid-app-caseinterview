# get python base
FROM python:3.10-slim-bookworm
ARG PIP_ACCESS_TOKEN
# use the same userid in the container as you have outside of the container
# this avoids permission conflicts when mounting volumes 
# as default use 1000/1000 as UID/GID, but they can be changed at build time if required
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN useradd -ms /bin/bash me

# set the permissions for the UID/GID
RUN if [ "$USER_GID" != "1000" ] || [ "$USER_UID" != "1000" ]; then groupmod --gid $USER_GID me && usermod --uid $USER_UID --gid $USER_GID me; fi

# run apt update/upgrade/install commands
# use buildkit cache directory 
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -qq
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get upgrade -yq

# Optionally install system packages, configure as required
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get install -yqq --no-install-recommends \
    git zsh curl postgresql-client lsof wget

RUN rm -rf /var/lib/apt/lists/*

# create .venv for user
ENV VIRTUAL_ENV=/home/me/.venv
RUN python3 -m venv $VIRTUAL_ENV --prompt myenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PIP_CACHE_DIR="/tmp/cache/pip"
RUN chown -R me:me /home/me

# run pip install with caching
RUN --mount=type=cache,target=/tmp/cache/pip \
    pip install --upgrade pip

# copy minimall installation files in /app
WORKDIR /app
COPY --chown=me:me setup.py .
COPY --chown=me:me setup.cfg .

# run pip install
RUN --mount=type=cache,target=/tmp/cache/pip \
    pip install -e .

# copy current directory in /app
COPY --chown=me:me . /app

# run pip install again with .git context for correct versioning
RUN --mount=type=cache,target=/tmp/cache/pip \
    pip install -e .

# change user and permissions
RUN chown -R me:me /home/me /app

USER me

EXPOSE 6543

CMD ["sh", "-c", "/app/entrypoint.sh"]
