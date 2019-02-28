from prometheus_client import Gauge
from prometheus_client import start_http_server

from huawei_lte_api.api.Monitoring import Monitoring
from huawei_lte_api.api.User import User
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection

from utils import get_environment_variable

import os
import time

router_username = get_environment_variable('ROUTER_USER')
router_password = get_environment_variable('ROUTER_PASSWORD')
router_host = get_environment_variable('ROUTER_HOST')
prometheus_port = int(get_environment_variable('PROMETHEUS_PORT', '9000'))
is_debug = bool(get_environment_variable('LOG_DEBUG', 'False'))
update_interval = float(get_environment_variable('ROUTER_POLL_INTERVAL', '1.5'))

gaugeDownloadRate = Gauge('router_download_rate_bytes', 'Download speed of the router')
gaugeUploadRate = Gauge('router_upload_rate_bytes', 'Upload speed of the router')
gaugeDownloadMonthTotal = Gauge('router_download_month_total_bytes', 'Download amount in this month')
gaugeUploadMonthTotal = Gauge('router_upload_month_total_bytes', 'Upload amount in this month')

data_store = {
    'CurrentDownloadRate': [],
    'CurrentUploadRate': []
}

median_count = 3

# connection = Connection('http://192.168.8.1/') For limited access, I have valid credentials no need for limited access

# client = Client(connection) # This just simplifies access to separate API groups, you can use device = Device(connection) if you want

# print(client.device.signal())  # Can be accessed without authorization
# print(client.device.information())  # Needs valid authorization, will throw exception if invalid credentials are passed in URL


# For more API calls just look on code in the huawei_lte_api/api folder, there is no separate DOC yet

def log(message: str):
    if is_debug:
        print(message)


def init_prometheus():
    print('initialize prometheus server on port ' + str(prometheus_port))
    start_http_server(prometheus_port)


def init_connection() -> AuthorizedConnection:
    print('initialize router connection')
    return AuthorizedConnection('http://' + router_host + "/", router_username, router_password)


def update_gauge_with_median(data: dict, router_data_key: str, gauge: Gauge):
    data_store[router_data_key].append(int(data[router_data_key]))
    list_length = len(data_store[router_data_key])
    if list_length > median_count:
        del data_store[router_data_key][0:list_length-median_count]
    average = 0
    for item in data_store[router_data_key]:
        average += item
    gauge.set(round(average/3, 2))


def update_metrics(con: AuthorizedConnection, downlist: list):
    traffic_stats = Monitoring(con).traffic_statistics()
    update_gauge_with_median(traffic_stats, 'CurrentDownloadRate', gaugeDownloadRate)
    update_gauge_with_median(traffic_stats, 'CurrentUploadRate', gaugeUploadRate)

try:
    init_prometheus()
    connection = init_connection()
    downloadlist = []
    while True:
        update_metrics(connection, downloadlist)
        time.sleep(update_interval)
finally:
    print('close connection')
    User(connection).logout()