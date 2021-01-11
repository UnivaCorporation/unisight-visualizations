# Unisight Data Bridge

This project holds a python application responsible for scraping data from
a Univa Unisight installation and then republishing it both as a 
[SimpleJSON](https://grafana.com/grafana/plugins/grafana-simple-json-datasource/installation)
and [Prometheus](https://prometheus.io/docs/visualization/grafana/) datasource.

# Design

This application contains two independent WSGI applicaitons that are merged into
one via WSGI application dispatching.  Each application is responsible for a given
set of metrics.  The `simplejson` app exposes scraped metrics via an Flask 
application meeting the needs of the SimpleJSON Grafana Datasource plugin.  The
`nodeexporter` application runs as a Prometheus client exporting custom generated
metrics.

# Running

This application can be run locally with `gunicorn` as follows:

    gunicorn -b 127.0.0.1:8001 \
        unisightDataBridge:create_app("unisight-server", 3000, "rest-user", "rest-password")

It can also be build and installed into a python environment and run with the
same command.
