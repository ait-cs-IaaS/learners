FROM python:3

RUN useradd --create-home --home-dir /opt/learners learners
USER learners

ARG LEARNERS_VERSION
ENV LEARNERS_VERSION=${LEARNERS_VERSION:-0.5.2}
ARG LEARNERS_BRANCH
ENV LEARNERS_BRANCH=${LEARNERS_BRANCH:-master}
ARG LEARNERS_CONFIG
ENV LEARNERS_CONFIG=${LEARNERS_CONFIG:-"/opt/learners/data/config.yml"}
ARG LEARNERS_PORT
ENV LEARNERS_PORT=${LEARNERS_PORT:-8080}

ENV PATH=${PATH}:/opt/learners/.local/bin

RUN git clone -b ${LEARNERS_BRANCH} --single-branch --depth 1 https://github.com/ait-cs-IaaS/learners /opt/learners/learners

# COPY --chown=learners * /opt/learners/

WORKDIR /opt/learners/learners

# RUN python -m pip install --upgrade pip wheel
RUN python -m pip install build
RUN python -m build
RUN pip install dist/Learners-${LEARNERS_VERSION}.tar.gz

# RUN pip install https://github.com/ait-cs-IaaS/learners/releases/download/${LEARNERS_VERSION}/Learners-${LEARNERS_VERSION}.tar.gz

RUN mkdir -p /opt/learners/webroot/uploads /opt/learners/webroot /opt/learners/data &&\
    ln -s /opt/learners/.local/lib/python3.10/site-packages/learners/templates /opt/learners/webroot/templates

VOLUME ["/opt/learners/webroot",\
        "/opt/learners/data/",\
        "/opt/learners/templates"]

EXPOSE ${LEARNERS_PORT}

WORKDIR /opt/learners

COPY ./entrypoint.sh /

CMD [ "/entrypoint.sh" ]
