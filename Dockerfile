#
# Tesseract 4 OCR Runtime Environment - Docker Container
#

FROM ubuntu:18.04

MAINTAINER "Shinri Ishikawa <github:QuadJust>"

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:alex-p/tesseract-ocr \
    && apt-get install -y tesseract-ocr-all \
      python3-pip \
      python3-distutils \
      mecab \
      libmecab-dev \
      mecab-ipadic-utf8 \
      swig \
      git \
      make \
      curl \
      xz-utils \
      file \
      sudo \
      wget \
      vim # for development

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /home/work
WORKDIR /home/work

RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git \
    && cd mecab-ipadic-neologd \
    && bin/install-mecab-ipadic-neologd -n -y

RUN mkdir app
COPY app app/

WORKDIR /home/work/app

RUN pip3 --no-cache-dir install -r requirements.txt

CMD ["python3", "index.py"]

EXPOSE 8080
