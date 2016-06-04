FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y python2.7 \
        python-pip

RUN apt-get autoremove -y && apt-get clean all
RUN pip install -U pip setuptools

COPY . /
#ENV MODE=DOCKER

RUN chmod +x *.sh
RUN pip install pymongo==3.2 \
        requests==2.9.1 \
        APScheduler==3.0.5 \
        gunicorn==19.4.5 \
        bottle==0.12.9 \
        gevent==1.1.1

EXPOSE 8080
ENTRYPOINT ["bash", "run.sh"]