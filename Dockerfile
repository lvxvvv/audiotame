# For Hugging Face (it is the same as Dockerfile.gradio):

FROM python:3.13-alpine

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk update --no-cache && apk upgrade --no-cache
RUN apk add --no-cache bash ffmpeg sox mp3gain

RUN python3 -m pip install --no-cache-dir --upgrade pip 
RUN python3 -m pip install --no-cache-dir audiotame[gui]

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENTRYPOINT ["audiotame"]
CMD ["--gradio"]

WORKDIR /tmp