FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ARG DOCKER_GID

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    sudo \
    libicu-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN ln -fs /usr/share/zoneinfo/Etc/GMT+1 /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata

RUN useradd -m runner && echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN groupadd -g ${DOCKER_GID} docker && usermod -aG docker runner

WORKDIR /home/runner

COPY github-runner.sh .
RUN chmod +x github-runner.sh

USER runner

ENTRYPOINT ["./github-runner.sh"]