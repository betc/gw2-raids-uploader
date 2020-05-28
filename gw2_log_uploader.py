import sys
import os
import requests
import json
import config
import time
from datetime import datetime, timedelta

BOSSES = [
    'Vale Guardian',
    'Gorseval',
    'Sabetha the Saboteur',
    'Slothasor',
    'Berg',
    'Matthias Gabrel',
    'Keep Construct',
    'Xera',
    'Cairn',
    'Mursaat Overseer',
    'Samarog',
    'Deimos',
    'Soulless Horror',
    'Dhuum',
    'Conjured Amalgamate',
    'Nikare',
    'Qadim'
]

FILE_PATH = os.path.normpath(config.LOGS_PATH)

RAIDAR_BASE_URL = 'https://www.gw2raidar.com/encounter/'
RAIDAR_REQUEST = 'https://www.gw2raidar.com/api/v2/encounters/new'
RAIDAR_REQUEST_ENCOUNTERS = 'https://www.gw2raidar.com/api/v2/encounters'
DPSREPORT_REQUEST = 'https://dps.report/uploadContent?json=1'


def upload_raidar(path):
    print("Uploading: " + path + " ", end="", flush=True)
    payload = {'file': open(path, 'rb')}
    res = requests.put(
        RAIDAR_REQUEST, headers=config.RAIDAR_HEADERS, files=payload)
    if res.status_code == 200:
        print(u'\u2713')
    else:
        print(u'\u2717')


def get_raidar_encounters(date, limit):
    date = datetime.strptime(date, "%Y%m%d")
    timestamp = str(int(time.mktime(date.timetuple())))
    cap = limit if limit > 0 else -1

    payload = {'limit': cap, 'since': timestamp}
    res = requests.get(RAIDAR_REQUEST_ENCOUNTERS,
                       headers=config.RAIDAR_HEADERS, params=payload)
    data = json.loads(res.content)

    logs = []
    for log in data['results']:
        logs.append(RAIDAR_BASE_URL + log['url_id'])

    return logs


def upload_dpsreport(path):
    payload = {'file': open(path, 'rb')}
    res = requests.post(DPSREPORT_REQUEST, files=payload)
    data = json.loads(res.content)
    return data['permalink']


def get_log_for_boss(base_path, fileList, date):
    date_start = datetime.strptime(date, "%Y%m%d").replace(hour=22)
    date_end = (date_start + timedelta(days=1)).replace(hour=4)

    logs = [file for file in fileList if date_start <= datetime.fromtimestamp(
        os.path.getmtime(base_path + '\\' + file)) <= date_end]
    if len(logs) > 0:
        file = logs[-1]
        return file


def parse_and_upload(date, dpsreport=True, gw2raidar=True):
    dps_report_logs = ['\n']

    for base_path, _, fileList in os.walk(FILE_PATH):
        parent = base_path.split('\\')[-2]
        if parent in BOSSES:
            log_name = get_log_for_boss(base_path, fileList, date)
            if log_name is not None:
                log_path = base_path + '\\' + log_name

                if dpsreport:
                    dps_report_logs.append(upload_dpsreport(log_path))

                if gw2raidar:
                    upload_raidar(log_path)

    if dpsreport:
        for line in dps_report_logs:
            print(line)

    # if gw2raidar:
    #   for line in get_raidar_encounters(date, len(dps_report_logs)):
    #     print(line)

    print("\nDone.")


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print(
            "Usage: py gw2_log_uploader.py [YYYYMMDD] -d (dpsreport) -r (gw2raidar) [-logs]")
    elif '-logs' in sys.argv:
        for line in get_raidar_encounters(sys.argv[1], 0):
            print(line)
    else:
        dpsreport = True if '-d' in sys.argv else False
        raidar = True if '-r' in sys.argv else False
        parse_and_upload(sys.argv[1], dpsreport, raidar)
