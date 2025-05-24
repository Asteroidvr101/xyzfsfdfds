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
def photonauth():
    AA = request.get_json()
    PlayFabId = AA.get("PlayFabId")
    OrgScopedID = AA.get("OrgScopedId")
    CustomId = AA.get("CustomID")
    Platform = AA.get("Platform")
    Nonce = AA.get("Nonce")
    UserId = AA.get("UserId")
    MasterPlayer = AA.get("Master")
    GorillaTagger = AA.get("GorillaTagger")
    CosmeticsInRoom = AA.get("CosmeticsInRoom")
    SharedGroupData = AA.get("SharedGroupData")
    UpdatePlayerCosmetics = AA.get("UpdatePlayerCosmetics")
    MasterClient = AA.get("MasterClient")
    ItemIds = AA.get("ItemIds")
    PlayerCount = AA.get("PlayerCount")
    CosmeticAuthenticationV2 = AA.get("CosmeticAuthenticationV2")
    RPCS = AA.get("RPCS")
    BroadcastMyRoomV2 = AA.get("BroadcastMyRoomV2")
    DLCOwnerShipV2 = AA.get("DLCOwnerShipV2")
    GorillaCorpCurrencyV1 = AA.get("GorillaCorpCurrencyV1")
    DeadMonke = AA.get("DeadMonke")
    GhostCounter = AA.get("GhostCounter")
    DirtyCosmeticSpawnnerV2 = AA.get("DirtyCosmeticSpawnnerV2")
    RoomJoined = AA.get("RoomJoined")
    VirtualStump = AA.get("VirtualStump")
    PlayerRoomCount = AA.get("PlayerRoomCount")
    AppVersion = AA.get("AppVersion")
    AppId = AA.get("AppId")
    TaggedDistance = AA.get("TaggedDistance")
    TaggedClient = AA.get("TaggedClient")
    OculusId = AA.get("OCULUSId")
    TitleId = AA.get("TITLE_ID")

    return jsonify({
        "ResultCode": 1,
        "StatusCode": 200,
        "Message": "authed with photon",
        "Result": 0,
        "UserId": UserId,
        "AppId": AppId,
        "AppVersion": AppVersion,
        "Ticket": AA.get("Ticket"),
        "Token": AA.get("Token"),
        "Nonce": Nonce,
        "Platform": Platform,
        "Username": AA.get("Username"),
        "PlayerRoomCount": PlayerRoomCount,
        "GorillaTagger": GorillaTagger,
        "CosmeticAuthentication": CosmeticAuthenticationV2,
        "CosmeticsInRoom": CosmeticsInRoom,
        "UpdatePlayerCosmetics": UpdatePlayerCosmetics,
        "DLCOwnerShip": DLCOwnerShipV2,
        "Currency": GorillaCorpCurrencyV1,
        "RoomJoined": RoomJoined,     
        "VirtualStump": VirtualStump,
        "DeadMonke": DeadMonke,
        "GhostCounter": GhostCounter,
        "BroadcastRoom": BroadcastMyRoomV2,
        "TaggedClient": TaggedClient,
        "TaggedDistance": TaggedDistance,
        "RPCS": RPCS
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
