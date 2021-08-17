FROM python:3.6

COPY . /unisight-visualizations
RUN ls -la /unisight-visualizations
RUN cd /unisight-visualizations/prometheus/unisight-data-bridge && python setup.py sdist

FROM centos:7
RUN yum update -y && yum install -y python3 python3-venv python3-pip

COPY --from=0 /unisight-visualizations/prometheus/unisight-data-bridge/dist/unisight-data-bridge-*.tar.gz /tmp

RUN python3 -m venv /opt/unisight-data-bridge
RUN . /opt/unisight-data-bridge/bin/activate && pip3 install `ls -t /tmp/unisight-data-bridge-*.tar.gz | head -n 1`

EXPOSE 8001

COPY prometheus/docker/init.sh /
CMD [ "/init.sh" ]
