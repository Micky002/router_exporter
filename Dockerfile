FROM python:3.7.2-alpine3.9

COPY router_monitor.py utils.py /

RUN pip install prometheus_client huawei-lte-api

ENV ROUTER_USER="admin" \
    ROUTER_PASSWORD="admin" \
    ROUTER_HOST="192.168.8.1" \
    PROMETHEUS_PORT="9000" \
    LOG_DEBUG="False" \
    ROUTER_POLL_INTERVAL="1.5"

CMD ["python", "./router_monitor.py"]