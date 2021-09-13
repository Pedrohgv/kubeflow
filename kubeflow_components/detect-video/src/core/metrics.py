from prometheus_client import Gauge, start_http_server


def start_prometheus_exposure(port=8000):
    start_http_server(port)


def counter(name, description):
    return Gauge(name=name, documentation=description)