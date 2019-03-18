#
# Tesseract 4 OCR Runtime Environment - Docker Container
#

FROM ubuntu:18.04

MAINTAINER "Shinri Ishikawa <github:QuadJust>"

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:alex-p/tesseract-ocr
RUN apt-get update && \
    apt-get install -y tesseract-ocr-all \
      wget \
      python3-distutils

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

RUN mkdir /home/work
WORKDIR /home/work

RUN mkdir app
COPY app app/

WORKDIR /home/work/app

RUN pip3 --no-cache-dir install -r requirements.txt

CMD ["python3", "index.py"]

EXPOSE 8080
