import datetime
from flask import Flask, request, jsonify
import requests
from werkzeug.datastructures import headers
from datetime import datetime, timedelta

class GameSettings:
    def __init__(self):
        self.TitleId: str = "3E875"
        self.SecretKey: str = "N5NTKHXEBMQ736KJASQ4PUEMW5CEIROOKF9Y9CKPHRP7B3M9I9"
        self.ApiKey: str = "OC|9951834934884203|b1e4d8e8c01190aacc38da98c8e1234e"

    def auth_headers(self):
        return {
            "Content-Type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = GameSettings()
app = Flask(__name__)

@app.route('/')
def index():
    return 'I Think The Backend Is Working'

@app.route('/api/PlayFabAuthentication', methods=['POST', 'GET'])
def playfab_auth():
    if 'UnityPlayer' not in request.headers['User-Agent']:
        return jsonify({
            "BanMessage": "Um What The Fuck",
            "BanExpirationTime": "Infinite"
        }), 403

    data = request.get_json()
    oculusid = data.get("OculusId")
    nonce = data.get("Nonce")
    appid = data.get("AppId")
    customid = data.get("CustomId")
    platform = data.get("Platform")

    requestlog = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
        headers=settings.auth_headers(),
        json={
            "CustomId": "OCULUS" + oculusid,
            "CreateAccount": True
        })
    if requestlog.status_code == 200:
            playerdata = requestlog.json()
            return jsonify({
                "PlayFabId": playerdata["data"]["PlayFabId"],
                "SessionTicket": playerdata["data"]["SessionTicket"],
                "EntityToken": playerdata["data"]["EntityToken"]["EntityToken"],
                "EntityId": playerdata["data"]["EntityToken"]["Entity"]["Id"],
                "EntityType": playerdata["data"]["EntityToken"]["Entity"]["Type"],
            }), 200
    else:
            if requestlog.status_code == 403:
                banshitty = requestlog.json()
                if banshitty.get('errorCode') == 1002:
                    banmessage = banshitty.get('errorMessage', 'No Message Found')
                    bandetails = banshitty.get('errorDetails', {})
                    banexpkey = next(iter(bandetails.keys()), None)
                    banexplist = bandetails.get(banexpkey, [])
                    banexp = banexplist[0] if len(banexplist) > 0 else 'Infinite'
                    print (banshitty)
                    return jsonify({
                        "BanMessage": banexpkey,
                        "BanExpirationTime": banexp
                    }), 403
@app.route('/api/CachePlayFabId', methods=['POST', 'GET'])
def cache_playfab_id():
    return 'PlayFabId I Think Um Whatever', 200

@app.route('/api/TitleData', methods=['GET', 'POST'])
def title_data():
    titlereq = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.auth_headers(),
    )

    if titlereq.status_code == 200:
        return jsonify(titlereq.json()), 200

@app.route("/api/CheckForBadName", methods=["POST", "GET"])
def check_for_bad_name():
        rjson = request.get_json() 
        function_result = rjson["FunctionArgument"]
        playfab_id = rjson["CallerEntityProfile"]["Lineage"]["MasterPlayerAccountId"]
        name = function_result["name"].upper()
        forRoom = function_result["forRoom"]

        if forRoom == True:
            return jsonify({"result": 0})

        link_response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Admin/UpdateUserTitleDisplayName",
            json={
                "DisplayName": name,
                "PlayFabId": playfab_id,
            },
            headers=settings.auth_headers(),
        ).json()
        return jsonify({"result": 0})


@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
        rjson = request.get_json()

        access_token = rjson.get("userToken")
        user_id = rjson.get("userID")
        nonce = rjson.get("nonce")
        sku = rjson.get("sku")

        response = requests.post(
            url=
            f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
            headers={"content-type": "application/json"})

        if response.json().get("success"):
            return jsonify({"result": True})
        else:
            return jsonify({"error": True})


@app.route("/api/photon", methods=["POST"])
def photon_authenticate():
    user_id = request.args.get("username")
    token = request.args.get("token")

    if user_id is None or len(user_id) != 16:
        return jsonify({'resultCode': 2, 'message': 'Invalid token', 'userId': None, 'nickname': None})

    if token is None:
        return jsonify({'resultCode': 3, 'message': 'Failed to parse token from request', 'userId': None, 'nickname': None})

    try:
        response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": user_id},
            headers=settings.get_auth_headers()
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'resultCode': 0, 'message': f"Something went wrong: {str(e)}", 'userId': None, 'nickname': None})

    try:
        user_info = response.json().get("UserInfo", {}).get("UserAccountInfo", {})
        nickname = user_info.get("Username", None)
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'resultCode': 0, 'message': f"Error parsing response: {str(e)}", 'userId': None, 'nickname': None})

    return jsonify({
        'resultCode': 1,
        'message': f'Authenticated user {user_id.lower()} title {settings.TitleId.lower()}',
        'userId': user_id.upper(),
        'nickname': nickname
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
