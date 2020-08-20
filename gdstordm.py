from flask import Flask, request
import requests, os
import urllib3

import base64
from pogoprotos.networking.responses.get_map_objects_response_pb2 import GetMapObjectsResponse #106
from pogoprotos.networking.responses.encounter_response_pb2 import EncounterResponse #102
from pogoprotos.networking.responses.get_holo_inventory_response_pb2 import GetHoloInventoryResponse #4
from pogoprotos.networking.responses.fort_search_response_pb2 import FortSearchResponse #101
from pogoprotos.networking.responses.fort_details_response_pb2 import FortDetailsResponse #104
from pogoprotos.networking.responses.gym_get_info_response_pb2 import GymGetInfoResponse # 156
from pogoprotos.networking.responses.get_player_response_pb2 import GetPlayerResponse #2
from google.protobuf.json_format import MessageToDict
import pprint

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

@app.route('/')
def homepage():
    return "Python GDSToRDM Connector V1.1"

@app.route("/raw", methods=["POST"])
def raw():
    data = request.get_json(force=True)
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
    for proto in items:
        #decode_raw_data(proto)
        method = proto.get('method')

    try:
        req = requests.post(url='http://'+RDM_URL+'/raw', json=data, headers=headers)
        if req.status_code not in [200,201]:
            print("[GDSTORDM] Status code: {}".format(req.status_code))
        print("[GDSTORDM] /RAW", devicename, ip_address, method, username, trainerlvl)
    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[GDSTORDM] RAW ERROR:", de)
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[GDSTORDM] RAW ERROR:", ce)
    return 'OK'

def decode_raw_data(proto):
    for datas in proto:
        Decode = base64.b64decode(proto['data'])
        if proto["method"] == 2:
            obj = GetPlayerResponse()
            obj.ParseFromString(Decode)
            object = MessageToDict(obj)
            pprint.pprint(object)

@app.route("/controler", methods=["POST"])
def controler():
    response = 'OK'

    data = request.get_json(force=True)
    ip_address = request.environ['REMOTE_ADDR']
    user_agent = request.user_agent.string

    type = data.get('type')
    username = data.get('username')
    uuid = data.get('uuid')

    print("[GDSTORDM] /CTR", uuid, ip_address, type, username)

    try:
        req = requests.post(url='http://'+RDM_URL+'/controler', json=data, headers=headers)
        if req.status_code not in [200,201]:
            print("[GDSTORDM] Status code: {}".format(req.status_code))
        json = req.json()
        data2 = json.get('data')

        unique_id = req.headers.get('X-Server')
        min_level = data2.get('min_level', 0)
        max_level = data2.get('max_level', 0)
        action = data2.get('action')
        lat = data2.get('lat')
        lon = data2.get('lon')

        if req.content:
            response = req.content

        print("[GDSTORDM] /RDM", RDM_URL, action, min_level, max_level, lat, lon)

    except urllib3.exceptions.ProtocolError as de:
        retry_error = True
        print("[GDSTORDM] CTR ERROR:", de)
    except requests.exceptions.ConnectionError as ce:
        retry_error = True
        print("[GDSTORDM] CTR ERROR:", ce)

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
