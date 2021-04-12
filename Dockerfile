FROM ubuntu:18.04

LABEL maintainer Team STINGAR <team-stingar@duke.edu>
LABEL name "hpfeeds-forwarder"
LABEL version "1.9"
LABEL release "1"
LABEL summary "Community Honey Network hpfeeds forwarder"
LABEL description "Small app for forwarding hpfeeds logs to another hpfeeds instance"
LABEL authoritative-source-url "https://github.com/CommunityHoneyNetwork/hpfeeds-forwarder"
LABEL changelog-url "https://github.com/CommunityHoneyNetwork/hpfeeds-forwarder/commits/master"

COPY requirements.txt /opt/requirements.txt
ENV DEBIAN_FRONTEND "noninteractive"

RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc git python3-dev python3-pip
RUN pip3 install -r /opt/requirements.txt
RUN pip3 install git+https://github.com/CommunityHoneyNetwork/hpfeeds3.git

ADD . /opt/
RUN chmod 755 /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]