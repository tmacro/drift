FROM gliderlabs/alpine:latest

RUN apk-install ffmpeg python3 grep

RUN mkdir /app /media/input /media/output
ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python3 drift.py
