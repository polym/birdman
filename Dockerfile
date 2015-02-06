FROM ubuntu:14.04
MAINTAINER Hongbo.Mo "hongbo.mo@upai.com"

ENV DEBIAN_FRONTEND noninteractive

RUN sed -i 's/archive.ubuntu.com/mirrors.163.com/' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y python-dev python-pip

RUN pip install gunicorn==18.0 UpYun setproctitle

EXPOSE 8888
