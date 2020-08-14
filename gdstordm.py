from flask import Flask, request
import requests, os

app = Flask(__name__, static_url_path='')

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

RDM_URL = "192.168.0.111:9001"
AUTH_TOKEN = 'YOURRDMTOKEN'

headers = {
    "User-Agent": "Python GDSToRDM Connector V1.1",
    "Authorization": "Bearer " + AUTH_TOKEN
}

@app.route("/raw", methods=["POST"])
def raw():
    data = request.json
    ip_address = request.environ['REMOTE_ADDR']
    user_agent = request.user_agent.string

    devicename = data.get('devicename')
    trainerexp = data.get('trainerexp')
    trainername = data.get('trainername')
    uuid = data.get('uuid')
    username = data.get('username')
    trainerlvl = data.get('trainerlvl')
    lat_target = data.get('lat_target')
    lon_target = data.get('lon_target')

    method = 0
    items = data.get('contents')
    for item in items:
        method = item.get('method')

    print("[GDSTORDM] /RAW", ip_address, user_agent, devicename, username, method, lat_target, lon_target)

    req = requests.post(url='http://'+RDM_URL+'/raw', json=data, headers=headers)
    if req.status_code not in [200,201]:
        print("Status code: {}".format(req.status_code))

    return 'OK'

@app.route("/controler", methods=["POST"])
def controler():
    data = request.get_json(force=True)
    ip_address = request.environ['REMOTE_ADDR']
    user_agent = request.user_agent.string

    type = data.get('type')
    username = data.get('username')
    uuid = data.get('uuid')

    print("[GDSTORDM] /CTR", ip_address, user_agent, uuid, username, type)

    req = requests.post(url='http://'+RDM_URL+'/controler', json=data, headers=headers)
    if req.status_code not in [200,201]:
        print("Status code: {}".format(req.status_code))

    unique_id = req.headers.get('X-Server')

    json = req.json()
    data2 = json.get('data')

    min_level = data2.get('min_level')
    max_level = data2.get('max_level')
    action = data2.get('action')
    lat = data2.get('lat')
    lon = data2.get('lon')

    print("[GDSTORDM] /RDM", RDM_URL, unique_id, req.elapsed, action, min_level, max_level, lat, lon)

    return req.content

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
