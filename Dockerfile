FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y python2.7 \
        python-pip \

RUN apt-get autoremove -y && apt-get clean all
RUN pip install -U pip setuptools
COPY . /
ENV MODE=DOCKER
RUN chmod +x *.sh
RUN pip install -r requeriments.txt

EXPOSE 8080
ENTRYPOINT ["sudo","run.sh"]