FROM python:slim

ADD . /tmp/tifft

RUN set -e \
      && pip install -U --no-cache-dir /tmp/tifft \
      && rm -rf /tmp/tifft

ENTRYPOINT ["/usr/local/bin/tifft"]
