FROM gliderlabs/alpine:latest

RUN apk-install ffmpeg python3

RUN mkdir /app
ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python3 drift.py
