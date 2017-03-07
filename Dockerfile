FROM alpine:latest
MAINTAINER Michael Bonnett, Jr. <mike_bonnett@yahoo.com>

RUN apk --no-cache add \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv

WORKDIR /app

COPY . /app
RUN virtualenv /env && /env/bin/pip install -r /app/requirements.txt

EXPOSE 5000
CMD ["/env/bin/python", "app.py"]
