FROM centos:7

RUN yum install -y python3 python3-venv python3-pip

RUN curl -L -O https://github.com/UnivaCorporation/unisight-visualizations/releases/download/v2.0.0/unisight-data-bridge-2.0.0.tar.gz

RUN python3 -m venv /opt/unisight-data-bridge
RUN . /opt/unisight-data-bridge/bin/activate && pip3 install unisight-data-bridge-2.0.0.tar.gz

EXPOSE 8001

COPY init.sh /
CMD [ "/init.sh" ]
