FROM python:3

RUN useradd --create-home --home-dir /opt/learners learners
USER learners

ENV PATH=${PATH}:/opt/learners/.local/bin
ENV LEARNERS_VERSION=${LEARNERS_VERSION:-0.5.1}

RUN python -m pip install --upgrade pip wheel &&\
    pip install https://github.com/ait-cs-IaaS/learners/releases/download/${LEARNERS_VERSION}/Learners-${LEARNERS_VERSION}.tar.gz

WORKDIR /opt/learners/

RUN mkdir -p webroot/uploads webroot/exercises webroot/documentation data &&\
    ln -s /opt/learners/.local/lib/python3.10/site-packages/learners/static webroot/static

ENV LEARNERS_CONFIG=/opt/learners/data/learners_config.yml

VOLUME ["/opt/learners/webroot/exercises",\
        "/opt/learners/webroot/documentation",\
        "/opt/learners/data/"\
       ]

EXPOSE ${LEARNERS_PORT:-8080}

COPY ./entrypoint.sh /

CMD [ "/entrypoint.sh" ]
