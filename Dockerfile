FROM ubuntu:18.04
MAINTAINER Marc Fouché <fouche.marc@gmail.com>

COPY build /tmp/build
RUN /tmp/build && rm -rf /tmp/build

COPY htmltopdf /htmltopdf

RUN groupadd -r celery && useradd --no-log-init -r -g celery celery

USER celery
WORKDIR /htmltopdf
ENTRYPOINT celery -A htmltopdf worker -l info
