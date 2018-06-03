FROM ubuntu:18.04

ENV LANG C.UTF-8

RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y byobu curl git htop man unzip vim wget && \
  apt-get install -y python3 python3-dev python3-pip && \
  rm -rf /var/lib/apt/lists/* \
  python3 setup.py develop

# Add files.
ADD . /root

RUN pip3 install -r /root/requirements-dev.txt

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
CMD ["python3", "eduzen_bot", "-v"]
