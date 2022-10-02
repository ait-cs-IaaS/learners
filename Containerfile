FROM python:3

RUN useradd --create-home --home-dir /opt/learners learners
USER learners

ENV PATH=${PATH}:/opt/learners/.local/bin
ENV LEARNERS_VERSION=${LEARNERS_VERSION:-0.6.1}
ENV LEARNERS_BRANCH=${LEARNERS_BRANCH}

RUN python -m pip install --upgrade pip wheel

RUN [ -z $LEARNERS_BRANCH ] &&\
    pip install https://github.com/ait-cs-IaaS/learners/releases/download/${LEARNERS_VERSION}/Learners-${LEARNERS_VERSION}.tar.gz ||\
    pip install https://github.com/ait-cs-IaaS/learners/archive/refs/heads/${LEARNERS_BRANCH}.zip

WORKDIR /opt/learners/

RUN mkdir -p webroot/uploads data &&\
    ln -s /opt/learners/.local/lib/python3.10/site-packages/learners/templates webroot/templates

ENV LEARNERS_CONFIG=/opt/learners/data/config.yml

VOLUME ["/opt/learners/webroot",\
        "/opt/learners/data/",\
        "/opt/learners/templates"]

EXPOSE ${LEARNERS_PORT:-8080}

COPY ./entrypoint.sh /

CMD [ "/entrypoint.sh" ]
