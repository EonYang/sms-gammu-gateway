FROM python:3-alpine

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/community' >> /etc/apk/repositories
RUN apk update
RUN apk add --no-cache pkgconfig gammu=1.39.0-r2 gammu-libs=1.39.0-r2  gammu-dev=1.39.0-r2
RUN mkdir ssl

WORKDIR /app

COPY requirements.txt ./
RUN apk add --no-cache --virtual .build-deps libffi-dev openssl-dev gcc musl-dev \
     && pip install -r requirements.txt \
     && apk del .build-deps libffi-dev openssl-dev gcc musl-dev

COPY ./ ./
RUN pip install -e .
ENTRYPOINT [ "python", "-m", "mail_me_my_sms.main" ]
