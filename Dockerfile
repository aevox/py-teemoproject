FROM ubuntu:18.04
MAINTAINER Marc Fouché <fouche.marc@gmail.com>

COPY build /tmp/build
RUN /tmp/build && rm -rf /tmp/build

COPY htmltopdf /htmltopdf

WORKDIR /htmltopdf
ENTRYPOINT celery -A htmltopdf  worker -l info
